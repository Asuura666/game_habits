"""
Badge Service - Gestion des badges et achievements.

Types de conditions de badges:
- streak: Nombre de jours consécutifs
- completions: Nombre total de complétions
- level: Niveau atteint
- time: Heure de complétion (early bird, night owl)
- combat_wins: Victoires PvP
- date: Date spécifique (saisonnier)
- secret: Conditions cachées
"""
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.badge import Badge, UserBadge
    from app.models.user import User


def check_all_badges(db: Session, user: "User") -> list["Badge"]:
    """
    Vérifie toutes les conditions de badges et débloque ceux mérités.
    
    Parcourt tous les badges disponibles et vérifie si l'utilisateur
    remplit les conditions pour chacun.
    
    Args:
        db: Session de base de données
        user: L'utilisateur à vérifier
        
    Returns:
        Liste des badges nouvellement débloqués
    """
    from app.models.badge import Badge, UserBadge
    
    # Récupérer tous les badges
    all_badges = db.query(Badge).all()
    
    # Récupérer les badges déjà obtenus
    user_badge_ids = {ub.badge_id for ub in user.badges}
    
    newly_unlocked = []
    
    for badge in all_badges:
        # Skip si déjà obtenu
        if badge.id in user_badge_ids:
            continue
        
        # Vérifier la condition
        if check_badge_condition(db, user, badge):
            unlock_badge(db, user, badge)
            newly_unlocked.append(badge)
    
    return newly_unlocked


def check_badge_condition(db: Session, user: "User", badge: "Badge") -> bool:
    """
    Vérifie si un utilisateur remplit la condition d'un badge.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        badge: Le badge à vérifier
        
    Returns:
        True si la condition est remplie
    """
    condition_type = badge.condition_type
    condition_value = badge.condition_value
    
    if condition_type == "streak":
        return _check_streak_condition(user, condition_value)
    
    elif condition_type == "completions":
        return _check_completions_condition(db, user, condition_value)
    
    elif condition_type == "level":
        return _check_level_condition(user, condition_value)
    
    elif condition_type == "time":
        return _check_time_condition(db, user, condition_value)
    
    elif condition_type == "combat_wins":
        return _check_combat_wins_condition(db, user, condition_value)
    
    elif condition_type == "date":
        return _check_date_condition(condition_value)
    
    elif condition_type == "coins":
        return _check_coins_condition(user, condition_value)
    
    elif condition_type == "habit_category":
        return _check_habit_category_condition(db, user, condition_value)
    
    elif condition_type == "friends":
        return _check_friends_condition(db, user, condition_value)
    
    elif condition_type == "secret":
        return _check_secret_condition(db, user, condition_value)
    
    return False


def _check_streak_condition(user: "User", condition: dict) -> bool:
    """Vérifie condition de streak."""
    required_streak = condition.get("min_streak", 0)
    return user.current_streak >= required_streak or user.best_streak >= required_streak


def _check_completions_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition de nombre de complétions."""
    from app.models.completion import Completion
    
    min_completions = condition.get("min_completions", 0)
    category = condition.get("category")  # Optionnel: filtre par catégorie
    
    query = db.query(Completion).filter(Completion.user_id == user.id)
    
    if category:
        from app.models.habit import Habit
        query = query.join(Habit).filter(Habit.category == category)
    
    total = query.count()
    return total >= min_completions


def _check_level_condition(user: "User", condition: dict) -> bool:
    """Vérifie condition de niveau."""
    required_level = condition.get("min_level", 0)
    return user.level >= required_level


def _check_time_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition d'heure de complétion."""
    from app.models.completion import Completion
    
    time_type = condition.get("time_type")  # "early_bird" ou "night_owl"
    required_count = condition.get("count", 1)
    
    query = db.query(Completion).filter(Completion.user_id == user.id)
    
    # Note: On vérifie l'heure de created_at
    completions = query.all()
    
    count = 0
    for completion in completions:
        hour = completion.created_at.hour
        
        if time_type == "early_bird" and 5 <= hour < 8:
            count += 1
        elif time_type == "night_owl" and 22 <= hour <= 23:
            count += 1
    
    return count >= required_count


def _check_combat_wins_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition de victoires en combat."""
    from app.models.combat import Combat
    
    required_wins = condition.get("min_wins", 0)
    
    wins = db.query(Combat).filter(
        Combat.winner_id == user.id,
        Combat.status == "completed"
    ).count()
    
    return wins >= required_wins


def _check_date_condition(condition: dict) -> bool:
    """Vérifie condition de date (badges saisonniers)."""
    today = date.today()
    
    # Vérifier si c'est une date spécifique
    target_date = condition.get("date")
    if target_date:
        target = datetime.strptime(target_date, "%m-%d").date().replace(year=today.year)
        return today == target
    
    # Vérifier si c'est une période (ex: Noël, Halloween)
    start_date = condition.get("start_date")
    end_date = condition.get("end_date")
    
    if start_date and end_date:
        start = datetime.strptime(start_date, "%m-%d").date().replace(year=today.year)
        end = datetime.strptime(end_date, "%m-%d").date().replace(year=today.year)
        return start <= today <= end
    
    return False


def _check_coins_condition(user: "User", condition: dict) -> bool:
    """Vérifie condition de coins accumulés."""
    # Note: On peut vérifier soit le total actuel, soit le total gagné
    required_coins = condition.get("min_coins", 0)
    check_type = condition.get("check_type", "current")  # "current" ou "total_earned"
    
    if check_type == "current":
        return user.coins >= required_coins
    
    # Pour total_earned, il faudrait sommer les CoinTransaction positives
    # Simplifié ici avec current
    return user.coins >= required_coins


def _check_habit_category_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition sur une catégorie d'habitude."""
    from app.models.habit import Habit
    from app.models.completion import Completion
    
    category = condition.get("category")
    min_completions = condition.get("min_completions", 0)
    
    if not category:
        return False
    
    count = db.query(Completion).join(Habit).filter(
        Completion.user_id == user.id,
        Habit.category == category
    ).count()
    
    return count >= min_completions


def _check_friends_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition sur les amis."""
    from app.models.friendship import Friendship
    
    min_friends = condition.get("min_friends", 0)
    
    friends_count = db.query(Friendship).filter(
        ((Friendship.requester_id == user.id) | (Friendship.addressee_id == user.id)),
        Friendship.status == "accepted"
    ).count()
    
    return friends_count >= min_friends


def _check_secret_condition(db: Session, user: "User", condition: dict) -> bool:
    """Vérifie condition secrète."""
    secret_type = condition.get("secret_type")
    
    if secret_type == "first_fail":
        # Badge pour la première habitude ratée
        from app.models.habit import Habit
        habits_with_reset = db.query(Habit).filter(
            Habit.user_id == user.id,
            Habit.current_streak == 0,
            Habit.total_completions > 0
        ).count()
        return habits_with_reset > 0
    
    elif secret_type == "comeback":
        # Revenir après 7+ jours d'absence
        if user.last_activity_date and user.current_streak == 1:
            # Complexe à vérifier, simplifié
            return True
    
    elif secret_type == "perfectionist":
        # 100% des habitudes du jour pendant 7 jours
        # Complexe, à implémenter avec plus de contexte
        pass
    
    return False


def unlock_badge(db: Session, user: "User", badge: "Badge") -> "UserBadge":
    """
    Débloque un badge pour un utilisateur.
    
    Crée l'entrée UserBadge et attribue les récompenses XP.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        badge: Le badge à débloquer
        
    Returns:
        L'objet UserBadge créé
    """
    from app.models.badge import UserBadge
    from app.services.xp_service import add_xp
    
    # Créer l'entrée UserBadge
    user_badge = UserBadge(
        user_id=user.id,
        badge_id=badge.id,
    )
    db.add(user_badge)
    
    # Attribuer la récompense XP
    if badge.xp_reward > 0:
        add_xp(
            db, user, badge.xp_reward, "badge", badge.id,
            f"Badge débloqué: {badge.name}"
        )
    
    return user_badge


def get_user_badges(db: Session, user: "User") -> list[dict]:
    """
    Récupère tous les badges d'un utilisateur avec leurs détails.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        
    Returns:
        Liste de dicts avec les infos des badges
    """
    badges_info = []
    
    for user_badge in user.badges:
        badge = user_badge.badge
        badges_info.append({
            "id": str(badge.id),
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "rarity": badge.rarity,
            "unlocked_at": user_badge.unlocked_at.isoformat(),
            "is_displayed": user_badge.is_displayed,
            "display_position": user_badge.display_position,
        })
    
    return badges_info


def get_available_badges(db: Session, user: "User") -> list[dict]:
    """
    Récupère les badges disponibles mais non encore obtenus.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        
    Returns:
        Liste de badges avec progression
    """
    from app.models.badge import Badge
    
    user_badge_ids = {ub.badge_id for ub in user.badges}
    available = []
    
    badges = db.query(Badge).filter(Badge.is_secret == False).all()
    
    for badge in badges:
        if badge.id in user_badge_ids:
            continue
        
        progress = _calculate_badge_progress(db, user, badge)
        
        available.append({
            "id": str(badge.id),
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "rarity": badge.rarity,
            "xp_reward": badge.xp_reward,
            "progress": progress,
        })
    
    return available


def _calculate_badge_progress(db: Session, user: "User", badge: "Badge") -> dict:
    """Calcule la progression vers un badge."""
    condition = badge.condition_value
    
    if badge.condition_type == "streak":
        current = max(user.current_streak, user.best_streak)
        target = condition.get("min_streak", 0)
        
    elif badge.condition_type == "completions":
        from app.models.completion import Completion
        current = db.query(Completion).filter(Completion.user_id == user.id).count()
        target = condition.get("min_completions", 0)
        
    elif badge.condition_type == "level":
        current = user.level
        target = condition.get("min_level", 0)
        
    elif badge.condition_type == "combat_wins":
        from app.models.combat import Combat
        current = db.query(Combat).filter(
            Combat.winner_id == user.id,
            Combat.status == "completed"
        ).count()
        target = condition.get("min_wins", 0)
        
    else:
        return {"current": 0, "target": 1, "percent": 0}
    
    percent = min(100, (current / target * 100)) if target > 0 else 0
    
    return {
        "current": current,
        "target": target,
        "percent": round(percent, 1),
    }


def set_displayed_badges(
    db: Session,
    user: "User",
    badge_ids: list[UUID]
) -> bool:
    """
    Définit les badges à afficher sur le profil (max 3).
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        badge_ids: Liste des IDs de badges à afficher (max 3)
        
    Returns:
        True si succès
    """
    from app.models.badge import UserBadge
    
    if len(badge_ids) > 3:
        badge_ids = badge_ids[:3]
    
    # Reset tous les displayed
    db.query(UserBadge).filter(
        UserBadge.user_id == user.id
    ).update({"is_displayed": False, "display_position": None})
    
    # Set les nouveaux
    for position, badge_id in enumerate(badge_ids, 1):
        db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == badge_id
        ).update({"is_displayed": True, "display_position": position})
    
    return True
