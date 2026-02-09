"""
Combat Router - PvP Challenges and Battles

Endpoints for challenging friends and viewing combat history.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUserWithCharacter, DBSession
from app.models.character import Character
from app.models.combat import Combat
from app.models.friendship import Friendship
from app.models.inventory import UserInventory
from app.models.transaction import CoinTransaction, XPTransaction
from app.models.user import User
from app.services.combat_service import CombatService

logger = structlog.get_logger()

router = APIRouter(prefix="/combat", tags=["Combat"])


# =============================================================================
# Response Models
# =============================================================================


class CombatParticipantResponse(BaseModel):
    """Combat participant info."""
    
    user_id: UUID
    username: str
    character_name: str
    character_class: str
    level: int
    avatar_url: str | None


class CombatLogEntry(BaseModel):
    """Single entry in combat log."""
    
    turn: int
    attacker_id: UUID
    defender_id: UUID
    action: str
    damage_dealt: int
    is_critical: bool
    is_dodge: bool
    attacker_hp: int
    defender_hp: int
    message: str


class CombatResponse(BaseModel):
    """Combat detail response."""
    
    id: UUID
    status: str
    challenger: CombatParticipantResponse
    defender: CombatParticipantResponse
    winner_id: UUID | None
    bet_coins: int
    total_turns: int | None
    winner_xp_reward: int
    winner_coins_reward: int
    combat_log: list[CombatLogEntry]
    created_at: datetime


class CombatSummaryResponse(BaseModel):
    """Combat summary for lists."""
    
    id: UUID
    status: str
    opponent_name: str
    opponent_class: str
    is_challenger: bool
    won: bool | None
    bet_coins: int
    xp_earned: int
    coins_earned: int
    total_turns: int | None
    created_at: datetime


class PendingChallengeResponse(BaseModel):
    """Pending challenge info."""
    
    id: UUID
    challenger_name: str
    challenger_class: str
    challenger_level: int
    bet_coins: int
    message: str | None
    expires_at: datetime
    created_at: datetime


class ChallengeCreateRequest(BaseModel):
    """Request to create a challenge."""
    
    bet_coins: int = Field(default=0, ge=0, le=1000, description="Coins to wager")
    message: str | None = Field(default=None, max_length=200)


class ChallengeCreateResponse(BaseModel):
    """Response after creating a challenge."""
    
    success: bool
    combat_id: UUID
    message: str


class CombatStatsResponse(BaseModel):
    """PvP statistics."""
    
    total_battles: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    current_win_streak: int
    best_win_streak: int
    total_xp_earned: int
    total_coins_earned: int
    total_coins_lost: int
    favorite_class_to_fight: str | None
    nemesis: str | None  # Most fought opponent


# =============================================================================
# Helper Functions
# =============================================================================


async def get_equipment_bonuses(db, user_id: UUID) -> dict[str, int]:
    """Get total equipment stat bonuses for a user."""
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.item))
        .where(
            UserInventory.user_id == user_id,
            UserInventory.is_equipped == True,
        )
    )
    entries = result.scalars().all()
    
    bonuses = {
        "strength": 0,
        "endurance": 0,
        "agility": 0,
        "intelligence": 0,
        "charisma": 0,
    }
    
    for entry in entries:
        bonuses["strength"] += entry.item.strength_bonus
        bonuses["endurance"] += entry.item.endurance_bonus
        bonuses["agility"] += entry.item.agility_bonus
        bonuses["intelligence"] += entry.item.intelligence_bonus
        bonuses["charisma"] += entry.item.charisma_bonus
    
    return bonuses


def combat_to_response(combat: Combat, current_user_id: UUID) -> CombatResponse:
    """Convert Combat model to response."""
    challenger_user = combat.challenger
    defender_user = combat.defender
    
    return CombatResponse(
        id=combat.id,
        status=combat.status,
        challenger=CombatParticipantResponse(
            user_id=challenger_user.id,
            username=challenger_user.username,
            character_name=combat.challenger_stats.get("name", "Unknown"),
            character_class=combat.challenger_stats.get("class", "unknown"),
            level=combat.challenger_stats.get("level", 1),
            avatar_url=challenger_user.avatar_url,
        ),
        defender=CombatParticipantResponse(
            user_id=defender_user.id,
            username=defender_user.username,
            character_name=combat.defender_stats.get("name", "Unknown"),
            character_class=combat.defender_stats.get("class", "unknown"),
            level=combat.defender_stats.get("level", 1),
            avatar_url=defender_user.avatar_url,
        ),
        winner_id=combat.winner_id,
        bet_coins=combat.bet_coins,
        total_turns=combat.total_turns,
        winner_xp_reward=combat.winner_xp_reward,
        winner_coins_reward=combat.winner_coins_reward,
        combat_log=[
            CombatLogEntry(**entry) for entry in combat.combat_log
        ],
        created_at=combat.created_at,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/challenge/{user_id}",
    response_model=ChallengeCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Challenge User",
    description="Challenge a friend to PvP combat.",
)
async def challenge_user(
    user_id: UUID,
    data: ChallengeCreateRequest,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> ChallengeCreateResponse:
    """Create a PvP challenge against a friend."""
    # Can't challenge yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot challenge yourself",
        )
    
    # Check if they are friends
    friendship_result = await db.execute(
        select(Friendship).where(
            Friendship.status == "accepted",
            or_(
                and_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == user_id,
                ),
                and_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == current_user.id,
                ),
            ),
        )
    )
    if not friendship_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only challenge friends",
        )
    
    # Get opponent
    opponent_result = await db.execute(
        select(User)
        .options(selectinload(User.character))
        .where(User.id == user_id, User.deleted_at.is_(None))
    )
    opponent = opponent_result.scalar_one_or_none()
    
    if not opponent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not opponent.character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Opponent has no character",
        )
    
    # Check bet amount
    if data.bet_coins > 0 and current_user.coins < data.bet_coins:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough coins. You have {current_user.coins}",
        )
    
    # Check for existing pending challenge
    pending_result = await db.execute(
        select(Combat).where(
            Combat.status == "pending",
            Combat.challenger_id == current_user.id,
            Combat.defender_id == user_id,
        )
    )
    if pending_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending challenge with this user",
        )
    
    # Get equipment bonuses
    challenger_bonuses = await get_equipment_bonuses(db, current_user.id)
    defender_bonuses = await get_equipment_bonuses(db, opponent.id)
    
    # Create combatants
    challenger_state = CombatService.create_combatant(
        current_user.character, challenger_bonuses
    )
    defender_state = CombatService.create_combatant(
        opponent.character, defender_bonuses
    )
    
    # Simulate combat
    result = CombatService.simulate_combat(
        challenger_state, defender_state, data.bet_coins
    )
    
    # Create combat record
    combat = Combat(
        challenger_id=current_user.id,
        defender_id=opponent.id,
        winner_id=result.winner_id,
        bet_coins=data.bet_coins,
        combat_log=result.combat_log,
        challenger_stats=result.challenger_stats,
        defender_stats=result.defender_stats,
        challenger_final_hp=result.challenger_final_hp,
        defender_final_hp=result.defender_final_hp,
        total_turns=result.total_turns,
        winner_xp_reward=result.winner_xp,
        winner_coins_reward=result.winner_coins,
        status="completed",
    )
    db.add(combat)
    
    # Apply rewards
    if result.winner_id:
        winner = current_user if result.winner_id == current_user.id else opponent
        loser = opponent if result.winner_id == current_user.id else current_user
        
        # Transfer coins
        if data.bet_coins > 0:
            loser.coins -= data.bet_coins
            winner.coins += result.winner_coins
            
            # Log transactions
            db.add(CoinTransaction(
                user_id=winner.id,
                amount=result.winner_coins,
                transaction_type="combat",
                reference_id=combat.id,
                description=f"Won combat against {loser.username}",
                balance_after=winner.coins,
            ))
            db.add(CoinTransaction(
                user_id=loser.id,
                amount=-data.bet_coins,
                transaction_type="combat",
                reference_id=combat.id,
                description=f"Lost combat against {winner.username}",
                balance_after=loser.coins,
            ))
        
        # Award XP
        winner.total_xp += result.winner_xp
        db.add(XPTransaction(
            user_id=winner.id,
            amount=result.winner_xp,
            source_type="combat",
            source_id=combat.id,
            description=f"Won combat against {loser.username}",
        ))
    
    await db.flush()
    
    logger.info(
        "Combat completed",
        combat_id=str(combat.id),
        challenger_id=str(current_user.id),
        defender_id=str(opponent.id),
        winner_id=str(result.winner_id) if result.winner_id else "draw",
    )
    
    return ChallengeCreateResponse(
        success=True,
        combat_id=combat.id,
        message=result.summary,
    )


@router.get(
    "/pending",
    response_model=list[PendingChallengeResponse],
    summary="Get Pending Challenges",
    description="Get challenges waiting for your response.",
)
async def get_pending_challenges(
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> list[PendingChallengeResponse]:
    """Get pending challenges where user is defender."""
    # Note: In current implementation, combats are instant
    # This endpoint would be used if we add async accept/decline
    result = await db.execute(
        select(Combat)
        .options(selectinload(Combat.challenger))
        .where(
            Combat.defender_id == current_user.id,
            Combat.status == "pending",
        )
        .order_by(Combat.created_at.desc())
    )
    combats = result.scalars().all()
    
    pending = []
    for combat in combats:
        pending.append(
            PendingChallengeResponse(
                id=combat.id,
                challenger_name=combat.challenger.username,
                challenger_class=combat.challenger_stats.get("class", "unknown"),
                challenger_level=combat.challenger_stats.get("level", 1),
                bet_coins=combat.bet_coins,
                message=None,  # TODO: Add message field to Combat
                expires_at=combat.created_at + timedelta(hours=24),
                created_at=combat.created_at,
            )
        )
    
    return pending


@router.get(
    "/history",
    response_model=list[CombatSummaryResponse],
    summary="Get Combat History",
    description="Get user's combat history.",
)
async def get_combat_history(
    current_user: CurrentUserWithCharacter,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
) -> list[CombatSummaryResponse]:
    """Get user's combat history."""
    result = await db.execute(
        select(Combat)
        .options(
            selectinload(Combat.challenger),
            selectinload(Combat.defender),
        )
        .where(
            Combat.status == "completed",
            or_(
                Combat.challenger_id == current_user.id,
                Combat.defender_id == current_user.id,
            ),
        )
        .order_by(Combat.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    combats = result.scalars().all()
    
    history = []
    for combat in combats:
        is_challenger = combat.challenger_id == current_user.id
        opponent = combat.defender if is_challenger else combat.challenger
        opponent_stats = combat.defender_stats if is_challenger else combat.challenger_stats
        
        won = None
        if combat.winner_id:
            won = combat.winner_id == current_user.id
        
        xp_earned = combat.winner_xp_reward if won else 0
        coins_earned = combat.winner_coins_reward if won else -combat.bet_coins if won is False else 0
        
        history.append(
            CombatSummaryResponse(
                id=combat.id,
                status=combat.status,
                opponent_name=opponent.username,
                opponent_class=opponent_stats.get("class", "unknown"),
                is_challenger=is_challenger,
                won=won,
                bet_coins=combat.bet_coins,
                xp_earned=xp_earned,
                coins_earned=coins_earned,
                total_turns=combat.total_turns,
                created_at=combat.created_at,
            )
        )
    
    return history


@router.get(
    "/stats",
    response_model=CombatStatsResponse,
    summary="Get Combat Stats",
    description="Get user's PvP statistics.",
)
async def get_combat_stats(
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> CombatStatsResponse:
    """Get user's PvP statistics."""
    # Get all user's completed combats
    result = await db.execute(
        select(Combat)
        .options(
            selectinload(Combat.challenger),
            selectinload(Combat.defender),
        )
        .where(
            Combat.status == "completed",
            or_(
                Combat.challenger_id == current_user.id,
                Combat.defender_id == current_user.id,
            ),
        )
        .order_by(Combat.created_at.desc())
    )
    combats = result.scalars().all()
    
    total = len(combats)
    wins = 0
    losses = 0
    draws = 0
    total_xp = 0
    total_coins_earned = 0
    total_coins_lost = 0
    opponent_classes: dict[str, int] = {}
    opponent_counts: dict[str, int] = {}
    
    current_streak = 0
    best_streak = 0
    streak_counting = True
    
    for combat in combats:
        is_challenger = combat.challenger_id == current_user.id
        opponent = combat.defender if is_challenger else combat.challenger
        opponent_stats = combat.defender_stats if is_challenger else combat.challenger_stats
        
        # Count opponent classes
        opp_class = opponent_stats.get("class", "unknown")
        opponent_classes[opp_class] = opponent_classes.get(opp_class, 0) + 1
        opponent_counts[opponent.username] = opponent_counts.get(opponent.username, 0) + 1
        
        if combat.winner_id == current_user.id:
            wins += 1
            total_xp += combat.winner_xp_reward
            total_coins_earned += combat.winner_coins_reward
            if streak_counting:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
        elif combat.winner_id is None:
            draws += 1
            streak_counting = False
        else:
            losses += 1
            total_coins_lost += combat.bet_coins
            streak_counting = False
    
    win_rate = (wins / total * 100) if total > 0 else 0.0
    
    favorite_class = max(opponent_classes, key=opponent_classes.get) if opponent_classes else None
    nemesis = max(opponent_counts, key=opponent_counts.get) if opponent_counts else None
    
    return CombatStatsResponse(
        total_battles=total,
        wins=wins,
        losses=losses,
        draws=draws,
        win_rate=round(win_rate, 1),
        current_win_streak=current_streak,
        best_win_streak=best_streak,
        total_xp_earned=total_xp,
        total_coins_earned=total_coins_earned,
        total_coins_lost=total_coins_lost,
        favorite_class_to_fight=favorite_class,
        nemesis=nemesis,
    )


@router.get(
    "/{combat_id}",
    response_model=CombatResponse,
    summary="Get Combat Details",
    description="Get detailed information about a specific combat.",
)
async def get_combat_details(
    combat_id: UUID,
    current_user: CurrentUserWithCharacter,
    db: DBSession,
) -> CombatResponse:
    """Get details of a specific combat."""
    result = await db.execute(
        select(Combat)
        .options(
            selectinload(Combat.challenger),
            selectinload(Combat.defender),
        )
        .where(Combat.id == combat_id)
    )
    combat = result.scalar_one_or_none()
    
    if not combat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat not found",
        )
    
    # Check if user was a participant
    if current_user.id not in [combat.challenger_id, combat.defender_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view combats you participated in",
        )
    
    return combat_to_response(combat, current_user.id)
