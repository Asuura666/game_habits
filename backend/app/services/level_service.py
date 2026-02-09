"""
Level Service - Gestion des niveaux et progression.

Formule de progression (inspirée RPG classique):
- XP requis = 100 * level^1.8
- Progression non-linéaire pour encourager l'engagement long terme

Récompenses par palier:
- Tous les niveaux: points de stats
- Paliers 5/10/25/50/100: récompenses spéciales
"""
import math
from typing import Any

# Coefficient de la formule XP
XP_BASE = 100
XP_EXPONENT = 1.8

# Points de stats par niveau
STAT_POINTS_PER_LEVEL = 2

# Récompenses spéciales par palier
MILESTONE_REWARDS = {
    5: {
        "stat_points": 5,
        "coins": 100,
        "title": "Apprenti Aventurier",
        "unlocked_items": ["basic_sword"],
    },
    10: {
        "stat_points": 5,
        "coins": 250,
        "title": "Aventurier",
        "unlocked_items": ["leather_armor"],
        "feature_unlock": "pvp_combat",
    },
    15: {
        "stat_points": 5,
        "coins": 400,
        "title": "Aventurier Confirmé",
        "unlocked_items": ["silver_ring"],
    },
    20: {
        "stat_points": 5,
        "coins": 600,
        "title": "Héros Local",
        "unlocked_items": ["steel_sword"],
    },
    25: {
        "stat_points": 10,
        "coins": 1000,
        "title": "Champion",
        "unlocked_items": ["champion_cape"],
        "feature_unlock": "guilds",
    },
    30: {
        "stat_points": 5,
        "coins": 800,
        "title": "Vétéran",
        "unlocked_items": ["veteran_helmet"],
    },
    40: {
        "stat_points": 5,
        "coins": 1200,
        "title": "Élite",
        "unlocked_items": ["elite_armor"],
    },
    50: {
        "stat_points": 15,
        "coins": 2000,
        "title": "Légende Vivante",
        "unlocked_items": ["legendary_sword", "golden_crown"],
        "feature_unlock": "custom_titles",
    },
    75: {
        "stat_points": 10,
        "coins": 3000,
        "title": "Mythique",
        "unlocked_items": ["mythic_wings"],
    },
    100: {
        "stat_points": 20,
        "coins": 5000,
        "title": "Immortel",
        "unlocked_items": ["immortal_aura", "god_slayer_blade"],
        "feature_unlock": "prestige_system",
    },
}


def xp_for_level(level: int) -> int:
    """
    Calcule l'XP total requis pour atteindre un niveau donné.
    
    Formule: XP = 100 * level^1.8
    
    Exemples:
    - Niveau 1: 0 XP (point de départ)
    - Niveau 2: 100 XP
    - Niveau 5: 871 XP
    - Niveau 10: 6,310 XP
    - Niveau 20: 44,090 XP
    - Niveau 50: 538,632 XP
    - Niveau 100: 3,981,072 XP
    
    Args:
        level: Le niveau cible (1+)
        
    Returns:
        XP total requis pour ce niveau
    """
    if level <= 1:
        return 0
    
    # XP cumulé pour atteindre ce niveau
    total_xp = 0
    for lvl in range(2, level + 1):
        total_xp += int(XP_BASE * (lvl ** XP_EXPONENT))
    
    return total_xp


def xp_for_next_level(current_level: int) -> int:
    """
    Calcule l'XP nécessaire pour passer du niveau actuel au suivant.
    
    Args:
        current_level: Niveau actuel
        
    Returns:
        XP requis pour le prochain niveau
    """
    return int(XP_BASE * ((current_level + 1) ** XP_EXPONENT))


def calculate_level_from_xp(total_xp: int) -> int:
    """
    Détermine le niveau basé sur l'XP total accumulé.
    
    Recherche binaire pour performance optimale.
    
    Args:
        total_xp: XP total de l'utilisateur
        
    Returns:
        Niveau correspondant (minimum 1)
    """
    if total_xp <= 0:
        return 1
    
    # Recherche binaire entre niveau 1 et 200 (cap raisonnable)
    low, high = 1, 200
    
    while low < high:
        mid = (low + high + 1) // 2
        if xp_for_level(mid) <= total_xp:
            low = mid
        else:
            high = mid - 1
    
    return low


def get_level_rewards(level: int) -> dict[str, Any]:
    """
    Retourne les récompenses pour un niveau donné.
    
    Combine les récompenses standards avec les récompenses de palier.
    
    Args:
        level: Le niveau atteint
        
    Returns:
        Dict contenant:
        - stat_points: Points de stats à allouer
        - coins: Pièces bonus
        - title: Titre débloqué (si palier)
        - unlocked_items: Items débloqués (si palier)
        - feature_unlock: Fonctionnalité débloquée (si palier)
    """
    rewards: dict[str, Any] = {
        "stat_points": STAT_POINTS_PER_LEVEL,
        "coins": 0,
        "title": None,
        "unlocked_items": [],
        "feature_unlock": None,
    }
    
    # Vérifier si c'est un palier spécial
    if level in MILESTONE_REWARDS:
        milestone = MILESTONE_REWARDS[level]
        rewards["stat_points"] = milestone.get("stat_points", STAT_POINTS_PER_LEVEL)
        rewards["coins"] = milestone.get("coins", 0)
        rewards["title"] = milestone.get("title")
        rewards["unlocked_items"] = milestone.get("unlocked_items", [])
        rewards["feature_unlock"] = milestone.get("feature_unlock")
    
    return rewards


def get_level_info(level: int) -> dict[str, Any]:
    """
    Retourne les informations complètes sur un niveau.
    
    Args:
        level: Le niveau
        
    Returns:
        Dict avec toutes les infos du niveau
    """
    xp_required = xp_for_level(level)
    xp_to_next = xp_for_next_level(level)
    rewards = get_level_rewards(level)
    
    # Déterminer le tier du personnage
    if level < 10:
        tier = "Débutant"
    elif level < 25:
        tier = "Intermédiaire"
    elif level < 50:
        tier = "Avancé"
    elif level < 75:
        tier = "Expert"
    elif level < 100:
        tier = "Maître"
    else:
        tier = "Légende"
    
    return {
        "level": level,
        "tier": tier,
        "xp_required": xp_required,
        "xp_to_next_level": xp_to_next,
        "rewards": rewards,
        "is_milestone": level in MILESTONE_REWARDS,
    }


def get_next_milestone(current_level: int) -> dict[str, Any] | None:
    """
    Retourne le prochain palier de récompenses.
    
    Args:
        current_level: Niveau actuel
        
    Returns:
        Dict du prochain palier ou None si niveau max atteint
    """
    milestones = sorted(MILESTONE_REWARDS.keys())
    
    for milestone in milestones:
        if milestone > current_level:
            xp_current = xp_for_level(current_level)
            xp_milestone = xp_for_level(milestone)
            
            return {
                "level": milestone,
                "xp_required": xp_milestone,
                "xp_remaining": xp_milestone - xp_current,
                "rewards": MILESTONE_REWARDS[milestone],
            }
    
    return None


def calculate_xp_table(max_level: int = 100) -> list[dict]:
    """
    Génère la table complète d'XP pour tous les niveaux.
    
    Utile pour debug ou affichage frontend.
    
    Args:
        max_level: Niveau maximum à calculer
        
    Returns:
        Liste de dicts avec level, xp_required, xp_to_next
    """
    table = []
    
    for level in range(1, max_level + 1):
        table.append({
            "level": level,
            "xp_total_required": xp_for_level(level),
            "xp_to_next": xp_for_next_level(level),
            "is_milestone": level in MILESTONE_REWARDS,
        })
    
    return table
