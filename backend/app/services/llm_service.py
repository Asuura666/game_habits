"""
LLM Service for AI-powered task evaluation.
Uses Anthropic Claude or OpenAI with function calling.
"""
import json
from decimal import Decimal
from typing import Any

import structlog
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas.task import Difficulty, TaskEvaluation

logger = structlog.get_logger()
settings = get_settings()


# Tool definitions for LLM function calling
EVALUATION_TOOLS = [
    {
        "name": "get_user_stats",
        "description": "Get user's current level, XP, streaks, and completion stats to calibrate task difficulty.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_similar_tasks",
        "description": "Find similar previously completed tasks to calibrate rewards based on historical data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to search for in task titles and descriptions",
                },
            },
            "required": ["keywords"],
        },
    },
    {
        "name": "get_reward_scale",
        "description": "Get the XP and coin reward scales for each difficulty level.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_category_average",
        "description": "Get average difficulty and time for tasks in a specific category.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Task category to get averages for",
                },
            },
            "required": ["category"],
        },
    },
]

# OpenAI format tools
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }
    for tool in EVALUATION_TOOLS
]

# Reward scales by difficulty
REWARD_SCALE = {
    "trivial": {"xp_min": 5, "xp_max": 15, "coins_min": 2, "coins_max": 5, "multiplier": 0.5},
    "easy": {"xp_min": 15, "xp_max": 35, "coins_min": 5, "coins_max": 15, "multiplier": 1.0},
    "medium": {"xp_min": 35, "xp_max": 75, "coins_min": 15, "coins_max": 35, "multiplier": 1.5},
    "hard": {"xp_min": 75, "xp_max": 150, "coins_min": 35, "coins_max": 75, "multiplier": 2.0},
    "epic": {"xp_min": 150, "xp_max": 300, "coins_min": 75, "coins_max": 150, "multiplier": 3.0},
    "legendary": {"xp_min": 300, "xp_max": 500, "coins_min": 150, "coins_max": 300, "multiplier": 5.0},
}


class LLMService:
    """Service for AI-powered task evaluation using Anthropic or OpenAI."""

    def __init__(self):
        """Initialize LLM clients based on configuration."""
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        if self.provider == "anthropic" and settings.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            self.openai_client = None
        elif settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.anthropic_client = None
            self.provider = "openai"
        else:
            raise ValueError("No LLM API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        
        logger.info("llm_service_initialized", provider=self.provider, model=self.model)

    async def evaluate_task(
        self,
        title: str,
        description: str | None,
        user_context: dict[str, Any],
    ) -> TaskEvaluation:
        """
        Evaluate a task using AI with function calling.
        
        Args:
            title: Task title
            description: Task description
            user_context: User data including stats, level, and history
            
        Returns:
            TaskEvaluation with difficulty, rewards, and suggestions
        """
        log = logger.bind(title=title, provider=self.provider)
        log.info("evaluating_task")
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(title, description, user_context)
        
        try:
            if self.provider == "anthropic":
                result = await self._evaluate_with_anthropic(
                    system_prompt, user_prompt, user_context
                )
            else:
                result = await self._evaluate_with_openai(
                    system_prompt, user_prompt, user_context
                )
            
            log.info("task_evaluated", difficulty=result.difficulty)
            return result
            
        except Exception as e:
            log.error("evaluation_failed", error=str(e))
            # Return sensible defaults on failure
            return self._get_default_evaluation()

    async def _evaluate_with_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        user_context: dict[str, Any],
    ) -> TaskEvaluation:
        """Evaluate using Anthropic Claude with tool use."""
        messages = [{"role": "user", "content": user_prompt}]
        
        # Initial API call
        response = await self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            tools=EVALUATION_TOOLS,
            messages=messages,
        )
        
        # Handle tool calls in a loop
        while response.stop_reason == "tool_use":
            # Process all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_result = await self._execute_tool(
                        block.name, block.input, user_context
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result),
                    })
            
            # Add assistant response and tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            # Continue conversation
            response = await self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                tools=EVALUATION_TOOLS,
                messages=messages,
            )
        
        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text
        
        return self._parse_evaluation(final_text)

    async def _evaluate_with_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        user_context: dict[str, Any],
    ) -> TaskEvaluation:
        """Evaluate using OpenAI with function calling."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Initial API call
        response = await self.openai_client.chat.completions.create(
            model=self.model if "gpt" in self.model else "gpt-4o-mini",
            max_tokens=1024,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        
        # Handle tool calls in a loop
        while message.tool_calls:
            messages.append(message)
            
            for tool_call in message.tool_calls:
                tool_result = await self._execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments),
                    user_context,
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                })
            
            # Continue conversation
            response = await self.openai_client.chat.completions.create(
                model=self.model if "gpt" in self.model else "gpt-4o-mini",
                max_tokens=1024,
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
            )
            message = response.choices[0].message
        
        return self._parse_evaluation(message.content or "")

    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            user_context: User context with stats and history
            
        Returns:
            Tool execution result as dict
        """
        log = logger.bind(tool=tool_name)
        log.debug("executing_tool", input=tool_input)
        
        try:
            if tool_name == "get_user_stats":
                return self._get_user_stats(user_context)
            
            elif tool_name == "get_similar_tasks":
                return self._get_similar_tasks(
                    tool_input.get("keywords", []),
                    user_context,
                )
            
            elif tool_name == "get_reward_scale":
                return self._get_reward_scale()
            
            elif tool_name == "get_category_average":
                return self._get_category_average(
                    tool_input.get("category", "general"),
                    user_context,
                )
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            log.error("tool_execution_failed", error=str(e))
            return {"error": str(e)}

    def _get_user_stats(self, user_context: dict[str, Any]) -> dict[str, Any]:
        """Get user statistics for calibration."""
        return {
            "level": user_context.get("level", 1),
            "total_xp": user_context.get("total_xp", 0),
            "current_streak": user_context.get("current_streak", 0),
            "best_streak": user_context.get("best_streak", 0),
            "tasks_completed_total": user_context.get("tasks_completed_total", 0),
            "tasks_completed_this_week": user_context.get("tasks_completed_this_week", 0),
            "average_completion_rate": user_context.get("average_completion_rate", 0.0),
            "preferred_difficulty": user_context.get("preferred_difficulty", "medium"),
        }

    def _get_similar_tasks(
        self,
        keywords: list[str],
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Find similar completed tasks for reference."""
        # This would query the database for similar tasks
        # For now, return data from context
        completed_tasks = user_context.get("completed_tasks", [])
        
        if not keywords or not completed_tasks:
            return {"similar_tasks": [], "message": "No similar tasks found"}
        
        # Simple keyword matching
        similar = []
        for task in completed_tasks[:10]:  # Limit to recent 10
            task_text = f"{task.get('title', '')} {task.get('description', '')}".lower()
            if any(kw.lower() in task_text for kw in keywords):
                similar.append({
                    "title": task.get("title"),
                    "difficulty": task.get("difficulty"),
                    "xp_reward": task.get("xp_reward"),
                    "coins_reward": task.get("coins_reward"),
                    "estimated_time": task.get("estimated_time_minutes"),
                })
        
        return {
            "similar_tasks": similar[:5],
            "count": len(similar),
        }

    def _get_reward_scale(self) -> dict[str, Any]:
        """Get the reward scale for each difficulty level."""
        return {
            "scale": REWARD_SCALE,
            "note": "Use these ranges to calibrate rewards. Higher in range for more complex/time-consuming tasks.",
        }

    def _get_category_average(
        self,
        category: str,
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Get average stats for tasks in a category."""
        category_stats = user_context.get("category_stats", {})
        
        if category in category_stats:
            return category_stats[category]
        
        # Default stats if category not found
        return {
            "category": category,
            "average_difficulty": "medium",
            "average_xp": 50,
            "average_time_minutes": 45,
            "task_count": 0,
            "message": "No historical data for this category",
        }

    def _build_system_prompt(self) -> str:
        """Build the system prompt for task evaluation."""
        return """You are an expert task evaluator for a gamified habit tracking app.

Your job is to analyze tasks and determine:
1. **Difficulty**: trivial, easy, medium, hard, epic, or legendary
2. **XP Reward**: Based on difficulty scale and task complexity
3. **Coin Reward**: Based on difficulty scale
4. **Estimated Time**: In minutes
5. **Subtasks**: Break down complex tasks into manageable steps

Use the available tools to:
- Check user stats to calibrate difficulty appropriately
- Find similar past tasks for consistent reward scaling
- Reference the reward scale for appropriate XP/coin values
- Check category averages for consistency

Be fair but challenging. Consider:
- Task complexity and skill required
- Time investment expected
- User's current level and experience
- Historical patterns from similar tasks

After gathering information, respond with a JSON object:
{
    "difficulty": "medium",
    "xp_reward": 50,
    "coins_reward": 25,
    "reasoning": "Brief explanation...",
    "suggested_subtasks": ["Step 1", "Step 2"],
    "estimated_time_minutes": 60
}"""

    def _build_user_prompt(
        self,
        title: str,
        description: str | None,
        user_context: dict[str, Any],
    ) -> str:
        """Build the user prompt with task details."""
        prompt = f"""Please evaluate this task:

**Title**: {title}
"""
        if description:
            prompt += f"""**Description**: {description}
"""
        
        category = user_context.get("category", "general")
        priority = user_context.get("priority", "medium")
        
        prompt += f"""
**Category**: {category}
**Priority**: {priority}

Use the available tools to gather context, then provide your evaluation as JSON."""
        
        return prompt

    def _parse_evaluation(self, text: str) -> TaskEvaluation:
        """
        Parse the LLM response into a TaskEvaluation.
        
        Args:
            text: Raw LLM response text
            
        Returns:
            Parsed TaskEvaluation object
        """
        log = logger.bind(response_length=len(text))
        
        try:
            # Try to extract JSON from the response
            # Handle markdown code blocks
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            elif "{" in text and "}" in text:
                # Find JSON object
                start = text.index("{")
                end = text.rindex("}") + 1
                json_str = text[start:end]
            else:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_str)
            
            # Map difficulty string to enum
            difficulty_str = data.get("difficulty", "medium").lower()
            try:
                difficulty = Difficulty(difficulty_str)
            except ValueError:
                difficulty = Difficulty.MEDIUM
            
            # Validate and clamp rewards
            xp_reward = max(1, min(1000, data.get("xp_reward", 50)))
            coins_reward = max(1, min(500, data.get("coins_reward", 25)))
            estimated_time = max(5, min(480, data.get("estimated_time_minutes", 60)))
            
            return TaskEvaluation(
                difficulty=difficulty,
                xp_reward=xp_reward,
                coins_reward=coins_reward,
                reasoning=data.get("reasoning", "Task evaluated based on complexity and time investment."),
                suggested_subtasks=data.get("suggested_subtasks", [])[:10],
                estimated_time_minutes=estimated_time,
            )
            
        except Exception as e:
            log.warning("parse_evaluation_failed", error=str(e))
            return self._get_default_evaluation()

    def _get_default_evaluation(self) -> TaskEvaluation:
        """Return a sensible default evaluation."""
        return TaskEvaluation(
            difficulty=Difficulty.MEDIUM,
            xp_reward=50,
            coins_reward=25,
            reasoning="Default evaluation - AI evaluation unavailable.",
            suggested_subtasks=[],
            estimated_time_minutes=60,
        )


# Singleton instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
