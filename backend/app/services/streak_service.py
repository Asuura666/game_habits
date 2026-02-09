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

from sqlalchemy.orm import Session

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


def update_streak(db: Session, user: "User", completion_date: date) -> dict:
    """
    Met à jour le streak de l'utilisateur après une activité.
    
    Logique:
    1. Si c'est le même jour que la dernière activité: pas de changement
    2. Si c'est le jour suivant: +1 streak
    3. Si plus d'un jour est passé: vérifie streak freeze, sinon reset
    
    Args:
        db: Session de base de données
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
        
    elif days_diff == 2 and check_streak_freeze(user):
        # Un jour manqué mais streak freeze disponible
        user.streak_freeze_available -= 1
        user.current_streak += 1  # On compte quand même aujourd'hui
        user.last_activity_date = completion_date
        result["new_streak"] = user.current_streak
        result["freeze_used"] = True
        
    elif days_diff > 1:
        # Streak perdu
        result["streak_lost"] = True
        
        # Sauvegarder le meilleur streak
        if user.current_streak > user.best_streak:
            user.best_streak = user.current_streak
        
        # Reset
        user.current_streak = 1
        user.last_activity_date = completion_date
        result["new_streak"] = 1
    
    # Vérifier les badges de streak
    if user.current_streak > result["old_streak"]:
        badges = check_streak_badges(db, user)
        result["badges_earned"] = badges
    
    return result


def check_streak_freeze(user: "User") -> bool:
    """
    Vérifie si l'utilisateur a un streak freeze disponible.
    
    Args:
        user: L'utilisateur
        
    Returns:
        True si freeze disponible, False sinon
    """
    return user.streak_freeze_available > 0


def use_streak_freeze(db: Session, user: "User") -> bool:
    """
    Utilise un streak freeze manuellement.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        
    Returns:
        True si utilisé avec succès, False si aucun disponible
    """
    if not check_streak_freeze(user):
        return False
    
    user.streak_freeze_available -= 1
    return True


def add_streak_freeze(db: Session, user: "User", amount: int = 1) -> int:
    """
    Ajoute des streak freezes à l'utilisateur.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        amount: Nombre de freezes à ajouter
        
    Returns:
        Nouveau total de freezes
    """
    user.streak_freeze_available += amount
    return user.streak_freeze_available


def get_streak_multiplier(streak: int) -> float:
    """
    Calcule le multiplicateur d'XP basé sur le streak.
    
    Formule: min(2.0, 1.0 + streak * 0.02)
    
    Exemples:
    - Streak 0: x1.0
    - Streak 5: x1.10
    - Streak 10: x1.20
    - Streak 25: x1.50
    - Streak 50+: x2.0 (cap)
    
    Args:
        streak: Nombre de jours de streak
        
    Returns:
        Multiplicateur (entre 1.0 et 2.0)
    """
    if streak <= 0:
        return STREAK_MULTIPLIER_MIN
    
    multiplier = STREAK_MULTIPLIER_MIN + (streak * STREAK_MULTIPLIER_INCREMENT)
    return min(STREAK_MULTIPLIER_MAX, multiplier)


def check_streak_badges(db: Session, user: "User") -> list["Badge"]:
    """
    Vérifie et débloque les badges de streak.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        
    Returns:
        Liste des badges nouvellement débloqués
    """
    from app.services.badge_service import unlock_badge
    from app.models.badge import Badge, UserBadge
    
    unlocked = []
    
    for threshold, badge_code in STREAK_BADGE_THRESHOLDS:
        if user.current_streak >= threshold:
            # Vérifier si déjà obtenu
            badge = db.query(Badge).filter(Badge.code == badge_code).first()
            
            if badge:
                existing = db.query(UserBadge).filter(
                    UserBadge.user_id == user.id,
                    UserBadge.badge_id == badge.id
                ).first()
                
                if not existing:
                    unlock_badge(db, user, badge)
                    unlocked.append(badge)
    
    return unlocked


def get_streak_status(user: "User") -> dict:
    """
    Retourne le statut complet du streak de l'utilisateur.
    
    Args:
        user: L'utilisateur
        
    Returns:
        Dict avec toutes les infos de streak
    """
    today = date.today()
    last_activity = user.last_activity_date
    
    # Déterminer si le streak est en danger
    streak_at_risk = False
    if last_activity:
        days_since = (today - last_activity).days
        streak_at_risk = days_since >= 1 and user.current_streak > 0
    
    # Prochain badge de streak
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
    """
    Calcule le coût en coins pour récupérer un streak perdu.
    
    Formule: 50 + (lost_streak * 10), max 1000 coins
    
    Args:
        lost_streak: Nombre de jours de streak perdus
        
    Returns:
        Coût en coins
    """
    base_cost = 50
    per_day_cost = 10
    max_cost = 1000
    
    cost = base_cost + (lost_streak * per_day_cost)
    return min(cost, max_cost)


def recover_streak(db: Session, user: "User", lost_streak: int) -> bool:
    """
    Tente de récupérer un streak perdu contre des coins.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        lost_streak: Streak à restaurer
        
    Returns:
        True si récupération réussie, False si pas assez de coins
    """
    cost = calculate_streak_recovery_cost(lost_streak)
    
    if user.coins < cost:
        return False
    
    user.coins -= cost
    user.current_streak = lost_streak
    user.last_activity_date = date.today() - timedelta(days=1)
    
    # Log la transaction
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
