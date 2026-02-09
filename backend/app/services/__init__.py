"""
Services métier du Habit Tracker RPG.

Ce module contient toute la logique métier de gamification:
- XP et progression
- Niveaux et récompenses
- Streaks et multiplicateurs
- Combat PvP
- Badges et achievements
- Classements (Redis)
"""

from app.services.xp_service import (
    calculate_habit_xp,
    calculate_task_xp,
    apply_streak_multiplier,
    apply_intelligence_bonus,
    add_xp,
    check_level_up,
    get_xp_progress,
)

from app.services.level_service import (
    xp_for_level,
    xp_for_next_level,
    calculate_level_from_xp,
    get_level_rewards,
    get_level_info,
    get_next_milestone,
)

from app.services.streak_service import (
    update_streak,
    check_streak_freeze,
    use_streak_freeze,
    add_streak_freeze,
    get_streak_multiplier,
    check_streak_badges,
    get_streak_status,
    calculate_streak_recovery_cost,
    recover_streak,
)

from app.services.combat_service import (
    CombatService,
    CombatantState,
    TurnResult,
    CombatResult,
)

from app.services.badge_service import (
    check_all_badges,
    check_badge_condition,
    unlock_badge,
    get_user_badges,
    get_available_badges,
    set_displayed_badges,
)

from app.services.leaderboard_service import (
    update_xp_leaderboard,
    update_streak_leaderboard,
    update_combat_leaderboard,
    get_leaderboard,
    get_friends_leaderboard,
    get_user_rank,
    check_rank_change,
    get_top_around_user,
    cleanup_old_leaderboards,
)

__all__ = [
    # XP Service
    "calculate_habit_xp",
    "calculate_task_xp",
    "apply_streak_multiplier",
    "apply_intelligence_bonus",
    "add_xp",
    "check_level_up",
    "get_xp_progress",
    # Level Service
    "xp_for_level",
    "xp_for_next_level",
    "calculate_level_from_xp",
    "get_level_rewards",
    "get_level_info",
    "get_next_milestone",
    # Streak Service
    "update_streak",
    "check_streak_freeze",
    "use_streak_freeze",
    "add_streak_freeze",
    "get_streak_multiplier",
    "check_streak_badges",
    "get_streak_status",
    "calculate_streak_recovery_cost",
    "recover_streak",
    # Combat Service
    "CombatService",
    "CombatantState",
    "TurnResult",
    "CombatResult",
    # Badge Service
    "check_all_badges",
    "check_badge_condition",
    "unlock_badge",
    "get_user_badges",
    "get_available_badges",
    "set_displayed_badges",
    # Leaderboard Service
    "update_xp_leaderboard",
    "update_streak_leaderboard",
    "update_combat_leaderboard",
    "get_leaderboard",
    "get_friends_leaderboard",
    "get_user_rank",
    "check_rank_change",
    "get_top_around_user",
    "cleanup_old_leaderboards",
]
