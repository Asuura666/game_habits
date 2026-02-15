"""
Streak Service - Gestion des séries de jours consécutifs.

Le streak représente le nombre de jours consécutifs où l'utilisateur
a complété au moins une habitude ou tâche.

Mécaniques:
- Streak augmente de 1 pour chaque jour actif consécutif
- Reset à 0 si un jour est manqué (sauf streak freeze)
- Streak freeze: protège 1 jour d'absence
- Multiplicateur XP: de x1.0 à x2.0 basé sur le streak
"""
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.models.badge import Badge, UserBadge
    from app.models.user import User

# Bornes du streak multiplier
STREAK_MULTIPLIER_MIN = 1.0
STREAK_MULTIPLIER_MAX = 2.0
STREAK_MULTIPLIER_INCREMENT = 0.02  # +2% par jour

# Badges de streak (jours consécutifs requis)
STREAK_BADGE_THRESHOLDS = [
    (7, "streak_week"),      # 1 semaine
    (14, "streak_2weeks"),   # 2 semaines
    (30, "streak_month"),    # 1 mois
    (60, "streak_2months"),  # 2 mois
    (90, "streak_quarter"),  # 3 mois
    (180, "streak_half"),    # 6 mois
    (365, "streak_year"),    # 1 an
]


async def update_streak(db: AsyncSession, user: "User", completion_date: date) -> dict:
    """
    Met à jour le streak de l'utilisateur après une activité.
    
    Args:
        db: Session async de base de données
        user: L'utilisateur
        completion_date: Date de l'activité
        
    Returns:
        Dict avec old_streak, new_streak, streak_lost, freeze_used
    """
    result = {
        "old_streak": user.current_streak,
        "new_streak": user.current_streak,
        "streak_lost": False,
        "freeze_used": False,
        "badges_earned": [],
    }
    
    last_activity = user.last_activity_date
    
    # Premier jour d'activité
    if last_activity is None:
        user.current_streak = 1
        user.last_activity_date = completion_date
        result["new_streak"] = 1
        if user.current_streak > user.best_streak:
            user.best_streak = user.current_streak
        return result
    
    # Même jour - pas de changement
    if last_activity == completion_date:
        return result
    
    days_diff = (completion_date - last_activity).days
    
    if days_diff == 1:
        # Jour consécutif - streak +1
        user.current_streak += 1
        user.last_activity_date = completion_date
        result["new_streak"] = user.current_streak
        if user.current_streak > user.best_streak:
            user.best_streak = user.current_streak
        
    elif days_diff == 2 and check_streak_freeze(user):
        # Un jour manqué mais streak freeze disponible
        user.streak_freeze_available -= 1
        user.current_streak += 1
        user.last_activity_date = completion_date
        result["new_streak"] = user.current_streak
        result["freeze_used"] = True
        if user.current_streak > user.best_streak:
            user.best_streak = user.current_streak
        
    elif days_diff > 1:
        # Streak perdu
        result["streak_lost"] = True
        if user.current_streak > user.best_streak:
            user.best_streak = user.current_streak
        user.current_streak = 1
        user.last_activity_date = completion_date
        result["new_streak"] = 1
    
    # Vérifier les badges de streak (async)
    if user.current_streak > result["old_streak"]:
        badges = await check_streak_badges(db, user)
        result["badges_earned"] = badges
    
    return result


def check_streak_freeze(user: "User") -> bool:
    """Vérifie si l'utilisateur a un streak freeze disponible."""
    return user.streak_freeze_available > 0


async def use_streak_freeze(db: AsyncSession, user: "User") -> bool:
    """Utilise un streak freeze manuellement."""
    if not check_streak_freeze(user):
        return False
    user.streak_freeze_available -= 1
    return True


async def add_streak_freeze(db: AsyncSession, user: "User", amount: int = 1) -> int:
    """Ajoute des streak freezes à l'utilisateur."""
    user.streak_freeze_available += amount
    return user.streak_freeze_available


def get_streak_multiplier(streak: int) -> float:
    """
    Calcule le multiplicateur d'XP basé sur le streak.
    
    Formule: min(2.0, 1.0 + streak * 0.02)
    """
    if streak <= 0:
        return STREAK_MULTIPLIER_MIN
    multiplier = STREAK_MULTIPLIER_MIN + (streak * STREAK_MULTIPLIER_INCREMENT)
    return min(STREAK_MULTIPLIER_MAX, multiplier)


async def check_streak_badges(db: AsyncSession, user: "User") -> list["Badge"]:
    """
    Vérifie et débloque les badges de streak (async version).
    
    Args:
        db: Session async de base de données
        user: L'utilisateur
        
    Returns:
        Liste des badges nouvellement débloqués
    """
    from app.models.badge import Badge, UserBadge
    
    unlocked = []
    
    for threshold, badge_code in STREAK_BADGE_THRESHOLDS:
        if user.current_streak >= threshold:
            # Vérifier si déjà obtenu - async
            badge_result = await db.execute(
                select(Badge).where(Badge.code == badge_code)
            )
            badge = badge_result.scalar_one_or_none()
            
            if badge:
                existing_result = await db.execute(
                    select(UserBadge).where(
                        UserBadge.user_id == user.id,
                        UserBadge.badge_id == badge.id
                    )
                )
                existing = existing_result.scalar_one_or_none()
                
                if not existing:
                    # Débloquer le badge
                    user_badge = UserBadge(
                        user_id=user.id,
                        badge_id=badge.id,
                    )
                    db.add(user_badge)
                    unlocked.append(badge)
    
    return unlocked


def get_streak_status(user: "User") -> dict:
    """Retourne le statut complet du streak de l'utilisateur."""
    today = date.today()
    last_activity = user.last_activity_date
    
    streak_at_risk = False
    if last_activity:
        days_since = (today - last_activity).days
        streak_at_risk = days_since >= 1 and user.current_streak > 0
    
    next_badge = None
    for threshold, badge_code in STREAK_BADGE_THRESHOLDS:
        if user.current_streak < threshold:
            next_badge = {
                "threshold": threshold,
                "badge_code": badge_code,
                "days_remaining": threshold - user.current_streak,
            }
            break
    
    return {
        "current_streak": user.current_streak,
        "best_streak": user.best_streak,
        "last_activity_date": last_activity.isoformat() if last_activity else None,
        "streak_multiplier": get_streak_multiplier(user.current_streak),
        "streak_freeze_available": user.streak_freeze_available,
        "streak_at_risk": streak_at_risk,
        "next_badge": next_badge,
    }


def calculate_streak_recovery_cost(lost_streak: int) -> int:
    """Calcule le coût en coins pour récupérer un streak perdu."""
    base_cost = 50
    per_day_cost = 10
    max_cost = 1000
    cost = base_cost + (lost_streak * per_day_cost)
    return min(cost, max_cost)


async def recover_streak(db: AsyncSession, user: "User", lost_streak: int) -> bool:
    """Tente de récupérer un streak perdu contre des coins."""
    cost = calculate_streak_recovery_cost(lost_streak)
    
    if user.coins < cost:
        return False
    
    user.coins -= cost
    user.current_streak = lost_streak
    user.last_activity_date = date.today() - timedelta(days=1)
    
    from app.models.transaction import CoinTransaction
    transaction = CoinTransaction(
        user_id=user.id,
        amount=-cost,
        transaction_type="streak_recovery",
        description=f"Récupération streak {lost_streak} jours",
        balance_after=user.coins,
    )
    db.add(transaction)
    
    return True
