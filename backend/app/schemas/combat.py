"""Combat schemas for PvP challenges and battles."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CombatStatus(str, Enum):
    """Status of a combat challenge."""
    
    PENDING = "pending"          # Waiting for opponent to accept
    ACCEPTED = "accepted"        # Challenge accepted, battle starting
    IN_PROGRESS = "in_progress"  # Battle ongoing
    COMPLETED = "completed"      # Battle finished
    DECLINED = "declined"        # Challenge was declined
    EXPIRED = "expired"          # Challenge timed out
    CANCELLED = "cancelled"      # Challenger cancelled


class CombatType(str, Enum):
    """Type of combat encounter."""
    
    PVP_DUEL = "pvp_duel"              # 1v1 player vs player
    BOSS_RAID = "boss_raid"            # Group vs AI boss
    HABIT_SHOWDOWN = "habit_showdown"  # Compare habit completion
    TASK_RACE = "task_race"            # Race to complete tasks


class ActionType(str, Enum):
    """Types of combat actions."""
    
    ATTACK = "attack"
    DEFEND = "defend"
    SKILL = "skill"
    ITEM = "item"
    FORFEIT = "forfeit"


class ChallengeCreate(BaseModel):
    """Schema for creating a combat challenge."""
    
    opponent_id: UUID = Field(
        ...,
        description="User ID of the opponent to challenge",
        examples=["550e8400-e29b-41d4-a716-446655440006"]
    )
    combat_type: CombatType = Field(
        default=CombatType.PVP_DUEL,
        description="Type of combat",
        examples=["pvp_duel", "habit_showdown"]
    )
    wager_coins: int = Field(
        default=0,
        ge=0,
        le=1000,
        description="Coins wagered on the outcome",
        examples=[100]
    )
    message: str | None = Field(
        default=None,
        max_length=200,
        description="Optional challenge message",
        examples=["Let's see who's the real habit master!"]
    )
    duration_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="For habit_showdown/task_race: duration in hours",
        examples=[24, 48]
    )


class CombatParticipant(BaseModel):
    """Information about a combat participant."""
    
    user_id: UUID = Field(
        ...,
        description="Participant's user ID"
    )
    character_name: str = Field(
        ...,
        description="Character name",
        examples=["Shadowbane"]
    )
    character_class: str = Field(
        ...,
        description="Character class",
        examples=["warrior"]
    )
    level: int = Field(
        ...,
        description="Character level",
        examples=[15]
    )
    current_hp: int = Field(
        ...,
        ge=0,
        description="Current HP in combat",
        examples=[85]
    )
    max_hp: int = Field(
        ...,
        ge=1,
        description="Maximum HP",
        examples=[100]
    )
    avatar_id: str = Field(
        ...,
        description="Avatar identifier"
    )


class CombatAction(BaseModel):
    """A single action in combat."""
    
    action_type: ActionType = Field(
        ...,
        description="Type of action"
    )
    skill_id: UUID | None = Field(
        default=None,
        description="Skill used (if action_type is skill)"
    )
    item_id: UUID | None = Field(
        default=None,
        description="Item used (if action_type is item)"
    )


class CombatTurn(BaseModel):
    """Schema for a single turn in combat."""
    
    turn_number: int = Field(
        ...,
        ge=1,
        description="Turn number",
        examples=[1]
    )
    attacker_id: UUID = Field(
        ...,
        description="Who performed the action"
    )
    defender_id: UUID = Field(
        ...,
        description="Who received the action"
    )
    action: ActionType = Field(
        ...,
        description="Action performed"
    )
    skill_name: str | None = Field(
        default=None,
        description="Name of skill used",
        examples=["Power Strike"]
    )
    damage_dealt: int = Field(
        default=0,
        ge=0,
        description="Damage dealt this turn",
        examples=[25]
    )
    damage_blocked: int = Field(
        default=0,
        ge=0,
        description="Damage blocked/mitigated",
        examples=[5]
    )
    healing_done: int = Field(
        default=0,
        ge=0,
        description="HP healed this turn",
        examples=[0]
    )
    is_critical: bool = Field(
        default=False,
        description="Whether the attack was critical"
    )
    is_miss: bool = Field(
        default=False,
        description="Whether the attack missed"
    )
    attacker_hp_after: int = Field(
        ...,
        ge=0,
        description="Attacker's HP after turn"
    )
    defender_hp_after: int = Field(
        ...,
        ge=0,
        description="Defender's HP after turn"
    )
    message: str = Field(
        ...,
        description="Turn description",
        examples=["Shadowbane used Power Strike for 25 damage!"]
    )
    timestamp: datetime = Field(
        ...,
        description="When the turn occurred"
    )


class CombatResult(BaseModel):
    """Final result of a combat encounter."""
    
    winner_id: UUID | None = Field(
        default=None,
        description="Winner's user ID (None if draw)"
    )
    loser_id: UUID | None = Field(
        default=None,
        description="Loser's user ID (None if draw)"
    )
    is_draw: bool = Field(
        default=False,
        description="Whether the battle ended in a draw"
    )
    winner_xp_earned: int = Field(
        default=0,
        ge=0,
        description="XP earned by winner",
        examples=[150]
    )
    loser_xp_earned: int = Field(
        default=0,
        ge=0,
        description="XP earned by loser (participation)",
        examples=[25]
    )
    coins_transferred: int = Field(
        default=0,
        ge=0,
        description="Coins transferred from loser to winner",
        examples=[100]
    )
    total_turns: int = Field(
        ...,
        ge=1,
        description="Total turns in the battle",
        examples=[12]
    )
    battle_duration_seconds: int = Field(
        ...,
        ge=0,
        description="Battle duration",
        examples=[180]
    )
    mvp_stat: str | None = Field(
        default=None,
        description="Most impactful stat in battle",
        examples=["strength", "agility"]
    )
    summary: str = Field(
        ...,
        description="Battle summary message",
        examples=["Shadowbane defeated DragonHeart in an epic 12-turn battle!"]
    )


class CombatResponse(BaseModel):
    """Schema for combat/challenge response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="Unique combat identifier",
        examples=["550e8400-e29b-41d4-a716-446655440007"]
    )
    combat_type: CombatType = Field(
        ...,
        description="Type of combat"
    )
    status: CombatStatus = Field(
        ...,
        description="Current combat status"
    )
    challenger: CombatParticipant = Field(
        ...,
        description="Challenge initiator"
    )
    opponent: CombatParticipant = Field(
        ...,
        description="Challenge recipient"
    )
    wager_coins: int = Field(
        default=0,
        description="Coins wagered"
    )
    message: str | None = Field(
        default=None,
        description="Challenge message"
    )
    turns: list[CombatTurn] = Field(
        default_factory=list,
        description="Combat turn history"
    )
    result: CombatResult | None = Field(
        default=None,
        description="Final result (if completed)"
    )
    current_turn: int = Field(
        default=0,
        ge=0,
        description="Current turn number"
    )
    whose_turn: UUID | None = Field(
        default=None,
        description="Whose turn it is (if in_progress)"
    )
    created_at: datetime = Field(
        ...,
        description="When challenge was created"
    )
    started_at: datetime | None = Field(
        default=None,
        description="When battle started"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When battle completed"
    )
    expires_at: datetime = Field(
        ...,
        description="When challenge expires"
    )


class ChallengeResponse(BaseModel):
    """Lightweight challenge response for listings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    combat_type: CombatType
    status: CombatStatus
    challenger_name: str
    opponent_name: str
    wager_coins: int
    created_at: datetime
    expires_at: datetime


class PerformActionRequest(BaseModel):
    """Request to perform a combat action."""
    
    combat_id: UUID = Field(
        ...,
        description="Combat to perform action in"
    )
    action: CombatAction = Field(
        ...,
        description="Action to perform"
    )
