"""
XP Service - Gestion de l'expérience et progression.

Formules basées sur le CDC:
- Habit XP: base 10-25 selon difficulté
- Task XP: évalué par IA (trivial=5, easy=15, medium=35, hard=70, epic=150, legendary=300)
- Streak multiplier: x1.0 à x2.0
- Intelligence bonus: +0.5% par point
"""
from datetime import datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.habit import Habit
    from app.models.task import Task
    from app.models.user import User

# XP de base par type de habitude (selon catégorie/difficulté)
HABIT_BASE_XP = {
    "easy": 10,
    "medium": 15,
    "hard": 20,
    "very_hard": 25,
}

# XP par difficulté de tâche (évalué par IA)
TASK_XP_BY_DIFFICULTY = {
    "trivial": 5,
    "easy": 15,
    "medium": 35,
    "hard": 70,
    "epic": 150,
    "legendary": 300,
}

# Bonus pour complétion en avance (% du XP de base)
EARLY_COMPLETION_BONUS = 0.20  # +20%

# Bornes du streak multiplier
STREAK_MULTIPLIER_MIN = 1.0
STREAK_MULTIPLIER_MAX = 2.0
STREAK_MULTIPLIER_INCREMENT = 0.02  # +2% par jour de streak

# Bonus intelligence (% par point)
INTELLIGENCE_BONUS_PER_POINT = 0.005  # +0.5% par point


def calculate_habit_xp(
    user: "User",
    habit: "Habit",
    completion_time: Optional[datetime] = None
) -> int:
    """
    Calcule l'XP gagné pour la complétion d'une habitude.
    
    Facteurs pris en compte:
    - XP de base selon la catégorie/difficulté
    - Multiplicateur de streak
    - Bonus d'intelligence du personnage
    - Bonus matinal (avant 9h) ou tard le soir (après 22h)
    
    Args:
        user: L'utilisateur qui complète l'habitude
        habit: L'habitude complétée
        completion_time: Heure de complétion (défaut: maintenant)
        
    Returns:
        XP calculé (entier)
    """
    if completion_time is None:
        completion_time = datetime.utcnow()
    
    # XP de base - utilise la catégorie ou défaut "medium"
    category_difficulty_map = {
        "health": "medium",
        "fitness": "hard",
        "learning": "hard",
        "mindfulness": "medium",
        "social": "easy",
        "productivity": "medium",
        "creativity": "medium",
        "general": "medium",
    }
    difficulty = category_difficulty_map.get(habit.category, "medium")
    base_xp = HABIT_BASE_XP.get(difficulty, 15)
    
    # Si l'habitude est quantifiable, ajuster selon le ratio de complétion
    # (géré ailleurs, ici on assume complétion à 100%)
    
    # Bonus horaire: +10% si matinal (6h-9h) ou nocturne (22h-00h)
    hour = completion_time.hour
    time_bonus = 0.0
    if 6 <= hour < 9:
        time_bonus = 0.10  # Early bird bonus
    elif 22 <= hour <= 23:
        time_bonus = 0.05  # Night owl petit bonus
    
    xp = base_xp * (1 + time_bonus)
    
    # Appliquer le multiplicateur de streak
    xp = apply_streak_multiplier(int(xp), user.current_streak)
    
    # Appliquer le bonus d'intelligence
    if user.character:
        xp = apply_intelligence_bonus(xp, user.character.intelligence)
    
    return int(xp)


def calculate_task_xp(task: "Task", completed_early: bool = False) -> int:
    """
    Calcule l'XP pour une tâche complétée.
    
    Utilise l'évaluation IA si disponible, sinon estimation par priorité.
    Bonus si complétée avant la deadline.
    
    Args:
        task: La tâche complétée
        completed_early: True si complétée avant la deadline
        
    Returns:
        XP calculé (entier)
    """
    # Utiliser le reward final si déjà calculé
    if task.final_xp_reward is not None:
        base_xp = task.final_xp_reward
    elif task.ai_xp_reward is not None:
        base_xp = task.ai_xp_reward + task.user_xp_adjustment
    elif task.ai_difficulty:
        base_xp = TASK_XP_BY_DIFFICULTY.get(task.ai_difficulty, 35)
    else:
        # Fallback basé sur la priorité
        priority_xp = {
            "low": 15,
            "medium": 35,
            "high": 70,
            "urgent": 100,
        }
        base_xp = priority_xp.get(task.priority, 35)
    
    # Bonus complétion en avance
    if completed_early:
        base_xp = int(base_xp * (1 + EARLY_COMPLETION_BONUS))
    
    return max(1, base_xp)


def apply_streak_multiplier(base_xp: int, streak: int) -> int:
    """
    Applique le multiplicateur de streak à l'XP de base.
    
    Formule: multiplier = min(2.0, 1.0 + streak * 0.02)
    - Streak 0: x1.0
    - Streak 25: x1.5
    - Streak 50+: x2.0 (cap)
    
    Args:
        base_xp: XP de base avant multiplicateur
        streak: Nombre de jours de streak
        
    Returns:
        XP après multiplicateur (entier)
    """
    from app.services.streak_service import get_streak_multiplier
    
    multiplier = get_streak_multiplier(streak)
    return int(base_xp * multiplier)


def apply_intelligence_bonus(xp: int, intelligence: int) -> int:
    """
    Applique le bonus d'intelligence à l'XP.
    
    Formule: xp * (1 + intelligence * 0.005)
    - 0 INT: +0%
    - 10 INT: +5%
    - 50 INT: +25%
    - 100 INT: +50%
    
    Args:
        xp: XP avant bonus
        intelligence: Stat d'intelligence du personnage
        
    Returns:
        XP après bonus (entier)
    """
    if intelligence <= 0:
        return xp
    
    bonus = 1 + (intelligence * INTELLIGENCE_BONUS_PER_POINT)
    return int(xp * bonus)


def add_xp(
    db: Session,
    user: "User",
    amount: int,
    source_type: str,
    source_id: Optional[UUID] = None,
    description: Optional[str] = None
) -> None:
    """
    Ajoute de l'XP à un utilisateur et enregistre la transaction.
    
    Vérifie automatiquement si l'utilisateur monte de niveau après l'ajout.
    
    Args:
        db: Session de base de données
        user: L'utilisateur qui reçoit l'XP
        amount: Quantité d'XP à ajouter (peut être négatif pour pénalités)
        source_type: Type de source (habit, task, combat, badge, streak, daily_bonus)
        source_id: ID optionnel de la source (habit_id, task_id, etc.)
        description: Description optionnelle de la transaction
    """
    from app.models.transaction import XPTransaction
    
    # Ajouter l'XP à l'utilisateur
    user.total_xp = max(0, user.total_xp + amount)
    
    # Créer la transaction d'audit
    transaction = XPTransaction(
        user_id=user.id,
        amount=amount,
        source_type=source_type,
        source_id=source_id,
        description=description,
    )
    db.add(transaction)
    
    # Vérifier level up
    leveled_up = check_level_up(db, user)
    
    # Commit géré par le caller
    return leveled_up


def check_level_up(db: Session, user: "User") -> bool:
    """
    Vérifie si l'utilisateur doit monter de niveau et applique le changement.
    
    Peut monter plusieurs niveaux d'un coup si beaucoup d'XP gagné.
    
    Args:
        db: Session de base de données
        user: L'utilisateur à vérifier
        
    Returns:
        True si au moins un level up, False sinon
    """
    from app.services.level_service import calculate_level_from_xp, get_level_rewards
    
    old_level = user.level
    new_level = calculate_level_from_xp(user.total_xp)
    
    if new_level > old_level:
        user.level = new_level
        
        # Attribuer les récompenses de chaque niveau gagné
        for level in range(old_level + 1, new_level + 1):
            rewards = get_level_rewards(level)
            
            # Points de stats à allouer
            if user.character and rewards.get("stat_points"):
                user.character.unallocated_points += rewards["stat_points"]
            
            # Coins bonus
            if rewards.get("coins"):
                user.coins += rewards["coins"]
            
            # Débloquer items (à implémenter avec inventory_service)
            # if rewards.get("unlocked_items"):
            #     for item_code in rewards["unlocked_items"]:
            #         unlock_item(db, user, item_code)
        
        return True
    
    return False


def get_xp_progress(user: "User") -> dict:
    """
    Retourne la progression XP de l'utilisateur vers le prochain niveau.
    
    Args:
        user: L'utilisateur
        
    Returns:
        Dict avec current_xp, xp_for_current_level, xp_for_next_level, progress_percent
    """
    from app.services.level_service import xp_for_level
    
    current_level_xp = xp_for_level(user.level)
    next_level_xp = xp_for_level(user.level + 1)
    
    xp_into_level = user.total_xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    
    progress = (xp_into_level / xp_needed * 100) if xp_needed > 0 else 100
    
    return {
        "total_xp": user.total_xp,
        "current_level": user.level,
        "xp_into_level": xp_into_level,
        "xp_for_next_level": xp_needed,
        "progress_percent": round(progress, 2),
    }
