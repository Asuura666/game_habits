"""
Combat Service - Simulation de combats PvP.

Système de combat tour par tour automatique:
- HP de base: 100 + (endurance * 5)
- Dégâts: force + weapon_bonus ± 20%
- Esquive: agility * 0.5% (cap 30%)
- Critique: intelligence * 0.3% (cap 20%)
- Dégâts critiques: x1.5

Le combat se termine quand un joueur atteint 0 HP ou après 50 tours (match nul).
"""
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.combat import Combat
    from app.models.user import User

# Configuration combat
BASE_HP = 100
HP_PER_ENDURANCE = 5
MAX_TURNS = 50

# Caps
MAX_DODGE_CHANCE = 0.30  # 30%
MAX_CRIT_CHANCE = 0.20   # 20%

# Multiplicateurs
CRIT_DAMAGE_MULTIPLIER = 1.5
DAMAGE_VARIANCE = 0.20  # ±20%

# Récompenses
BASE_XP_WIN = 50
BASE_COINS_WIN = 25
LOSER_XP_CONSOLATION = 10


@dataclass
class CombatStats:
    """Stats d'un combattant."""
    user_id: UUID
    username: str
    max_hp: int
    current_hp: int
    strength: int
    endurance: int
    agility: int
    intelligence: int
    weapon_bonus: int = 0
    armor_bonus: int = 0
    
    def to_dict(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "username": self.username,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "strength": self.strength,
            "endurance": self.endurance,
            "agility": self.agility,
            "intelligence": self.intelligence,
            "weapon_bonus": self.weapon_bonus,
            "armor_bonus": self.armor_bonus,
        }


@dataclass
class CombatResult:
    """Résultat d'un combat."""
    winner_id: Optional[UUID]
    loser_id: Optional[UUID]
    is_draw: bool
    challenger_final_hp: int
    defender_final_hp: int
    total_turns: int
    combat_log: list[dict] = field(default_factory=list)
    xp_rewards: dict = field(default_factory=dict)
    coin_rewards: dict = field(default_factory=dict)


def get_combat_stats(user: "User") -> CombatStats:
    """
    Extrait les stats de combat d'un utilisateur.
    
    Args:
        user: L'utilisateur
        
    Returns:
        CombatStats avec toutes les stats
    """
    character = user.character
    
    if not character:
        # Stats par défaut si pas de personnage
        return CombatStats(
            user_id=user.id,
            username=user.username,
            max_hp=BASE_HP,
            current_hp=BASE_HP,
            strength=5,
            endurance=5,
            agility=5,
            intelligence=5,
        )
    
    # Calculer HP max
    max_hp = BASE_HP + (character.endurance * HP_PER_ENDURANCE)
    
    # TODO: Récupérer bonus d'équipement depuis inventory
    weapon_bonus = 0
    armor_bonus = 0
    
    return CombatStats(
        user_id=user.id,
        username=user.username,
        max_hp=max_hp,
        current_hp=max_hp,
        strength=character.strength,
        endurance=character.endurance,
        agility=character.agility,
        intelligence=character.intelligence,
        weapon_bonus=weapon_bonus,
        armor_bonus=armor_bonus,
    )


def calculate_damage(attacker_stats: CombatStats, defender_stats: CombatStats) -> tuple[int, bool, bool]:
    """
    Calcule les dégâts d'une attaque.
    
    Args:
        attacker_stats: Stats de l'attaquant
        defender_stats: Stats du défenseur
        
    Returns:
        Tuple (damage, is_crit, is_dodged)
    """
    # Vérifier esquive
    dodge_chance = calculate_dodge_chance(defender_stats.agility)
    if random.random() < dodge_chance:
        return (0, False, True)
    
    # Dégâts de base
    base_damage = attacker_stats.strength + attacker_stats.weapon_bonus
    
    # Variance aléatoire ±20%
    variance = random.uniform(1 - DAMAGE_VARIANCE, 1 + DAMAGE_VARIANCE)
    damage = int(base_damage * variance)
    
    # Vérifier critique
    is_crit = False
    crit_chance = calculate_crit_chance(attacker_stats.intelligence)
    if random.random() < crit_chance:
        damage = int(damage * CRIT_DAMAGE_MULTIPLIER)
        is_crit = True
    
    # Réduction par armure (simple: -10% par 5 points d'armor_bonus)
    armor_reduction = min(0.5, defender_stats.armor_bonus * 0.02)  # Cap 50%
    damage = int(damage * (1 - armor_reduction))
    
    # Minimum 1 dégât
    damage = max(1, damage)
    
    return (damage, is_crit, False)


def calculate_dodge_chance(agility: int) -> float:
    """
    Calcule la chance d'esquive basée sur l'agilité.
    
    Formule: agility * 0.5%, cap à 30%
    
    Exemples:
    - Agility 10: 5%
    - Agility 30: 15%
    - Agility 60+: 30% (cap)
    
    Args:
        agility: Stat d'agilité
        
    Returns:
        Probabilité d'esquive (0.0 à 0.30)
    """
    chance = agility * 0.005  # 0.5% par point
    return min(MAX_DODGE_CHANCE, chance)


def calculate_crit_chance(intelligence: int) -> float:
    """
    Calcule la chance de coup critique basée sur l'intelligence.
    
    Formule: intelligence * 0.3%, cap à 20%
    
    Exemples:
    - Intelligence 10: 3%
    - Intelligence 30: 9%
    - Intelligence 67+: 20% (cap)
    
    Args:
        intelligence: Stat d'intelligence
        
    Returns:
        Probabilité de critique (0.0 à 0.20)
    """
    chance = intelligence * 0.003  # 0.3% par point
    return min(MAX_CRIT_CHANCE, chance)


def simulate_combat(challenger: "User", defender: "User") -> CombatResult:
    """
    Simule un combat PvP complet entre deux joueurs.
    
    Le combat est automatique, tour par tour:
    1. Le challenger attaque en premier
    2. Le défenseur contre-attaque s'il survit
    3. Répéter jusqu'à KO ou max turns
    
    Args:
        challenger: L'utilisateur qui défie
        defender: L'utilisateur défié
        
    Returns:
        CombatResult avec tous les détails du combat
    """
    challenger_stats = get_combat_stats(challenger)
    defender_stats = get_combat_stats(defender)
    
    combat_log = []
    turn = 0
    
    # Déterminer qui attaque en premier (plus haute agilité)
    attacker_first = challenger_stats.agility >= defender_stats.agility
    
    while turn < MAX_TURNS:
        turn += 1
        
        # Tour de l'attaquant actuel
        if attacker_first or turn > 1:
            # Challenger attaque
            damage, is_crit, is_dodged = calculate_damage(challenger_stats, defender_stats)
            
            log_entry = {
                "turn": turn,
                "attacker": "challenger",
                "attacker_name": challenger_stats.username,
                "defender_name": defender_stats.username,
                "damage": damage,
                "is_critical": is_crit,
                "is_dodged": is_dodged,
            }
            
            if not is_dodged:
                defender_stats.current_hp -= damage
                log_entry["defender_hp_remaining"] = max(0, defender_stats.current_hp)
            else:
                log_entry["defender_hp_remaining"] = defender_stats.current_hp
            
            combat_log.append(log_entry)
            
            # Vérifier KO
            if defender_stats.current_hp <= 0:
                break
        
        # Defender contre-attaque
        damage, is_crit, is_dodged = calculate_damage(defender_stats, challenger_stats)
        
        log_entry = {
            "turn": turn,
            "attacker": "defender",
            "attacker_name": defender_stats.username,
            "defender_name": challenger_stats.username,
            "damage": damage,
            "is_critical": is_crit,
            "is_dodged": is_dodged,
        }
        
        if not is_dodged:
            challenger_stats.current_hp -= damage
            log_entry["defender_hp_remaining"] = max(0, challenger_stats.current_hp)
        else:
            log_entry["defender_hp_remaining"] = challenger_stats.current_hp
        
        combat_log.append(log_entry)
        
        # Vérifier KO
        if challenger_stats.current_hp <= 0:
            break
        
        attacker_first = True  # Après le premier tour, alternance normale
    
    # Déterminer le gagnant
    if challenger_stats.current_hp <= 0 and defender_stats.current_hp <= 0:
        # Double KO - match nul
        winner_id = None
        loser_id = None
        is_draw = True
    elif defender_stats.current_hp <= 0:
        winner_id = challenger.id
        loser_id = defender.id
        is_draw = False
    elif challenger_stats.current_hp <= 0:
        winner_id = defender.id
        loser_id = challenger.id
        is_draw = False
    else:
        # Temps écoulé - celui avec le plus de HP % gagne
        challenger_hp_pct = challenger_stats.current_hp / challenger_stats.max_hp
        defender_hp_pct = defender_stats.current_hp / defender_stats.max_hp
        
        if challenger_hp_pct > defender_hp_pct:
            winner_id = challenger.id
            loser_id = defender.id
            is_draw = False
        elif defender_hp_pct > challenger_hp_pct:
            winner_id = defender.id
            loser_id = challenger.id
            is_draw = False
        else:
            winner_id = None
            loser_id = None
            is_draw = True
    
    return CombatResult(
        winner_id=winner_id,
        loser_id=loser_id,
        is_draw=is_draw,
        challenger_final_hp=max(0, challenger_stats.current_hp),
        defender_final_hp=max(0, defender_stats.current_hp),
        total_turns=turn,
        combat_log=combat_log,
    )


def distribute_rewards(
    db: Session,
    winner: "User",
    loser: "User",
    bet_coins: int = 0
) -> dict[str, Any]:
    """
    Distribue les récompenses après un combat.
    
    Le gagnant reçoit:
    - XP de base + bonus selon niveau du perdant
    - Coins de mise + bonus
    
    Le perdant reçoit:
    - XP de consolation
    - Perd la mise
    
    Args:
        db: Session de base de données
        winner: L'utilisateur gagnant
        loser: L'utilisateur perdant
        bet_coins: Mise en jeu
        
    Returns:
        Dict avec les récompenses distribuées
    """
    from app.services.xp_service import add_xp
    from app.models.transaction import CoinTransaction
    
    # Calculer XP du gagnant (bonus si le perdant est de niveau supérieur)
    level_diff = loser.level - winner.level
    level_bonus = max(0, level_diff * 10)  # +10 XP par niveau au-dessus
    winner_xp = BASE_XP_WIN + level_bonus
    
    # Calculer coins du gagnant
    winner_coins = BASE_COINS_WIN + bet_coins
    
    # Appliquer au gagnant
    add_xp(db, winner, winner_xp, "combat", None, f"Victoire PvP contre {loser.username}")
    winner.coins += winner_coins
    
    # Log transaction coins gagnant
    winner_coin_tx = CoinTransaction(
        user_id=winner.id,
        amount=winner_coins,
        transaction_type="combat",
        description=f"Victoire PvP contre {loser.username}",
        balance_after=winner.coins,
    )
    db.add(winner_coin_tx)
    
    # XP de consolation pour le perdant
    add_xp(db, loser, LOSER_XP_CONSOLATION, "combat", None, f"Défaite PvP contre {winner.username}")
    
    # Perdant perd la mise
    if bet_coins > 0:
        loser.coins = max(0, loser.coins - bet_coins)
        loser_coin_tx = CoinTransaction(
            user_id=loser.id,
            amount=-bet_coins,
            transaction_type="combat",
            description=f"Mise perdue PvP contre {winner.username}",
            balance_after=loser.coins,
        )
        db.add(loser_coin_tx)
    
    return {
        "winner": {
            "user_id": str(winner.id),
            "xp_earned": winner_xp,
            "coins_earned": winner_coins,
        },
        "loser": {
            "user_id": str(loser.id),
            "xp_earned": LOSER_XP_CONSOLATION,
            "coins_lost": bet_coins,
        },
    }


def create_combat_record(
    db: Session,
    challenger: "User",
    defender: "User",
    result: CombatResult,
    bet_coins: int = 0
) -> "Combat":
    """
    Crée l'enregistrement du combat en base de données.
    
    Args:
        db: Session de base de données
        challenger: Challenger
        defender: Défenseur
        result: Résultat du combat
        bet_coins: Mise en jeu
        
    Returns:
        L'objet Combat créé
    """
    from app.models.combat import Combat
    
    challenger_stats = get_combat_stats(challenger)
    defender_stats = get_combat_stats(defender)
    
    # Distribuer les récompenses si pas match nul
    rewards = {"winner": {}, "loser": {}}
    if not result.is_draw and result.winner_id:
        winner = challenger if result.winner_id == challenger.id else defender
        loser = defender if result.winner_id == challenger.id else challenger
        rewards = distribute_rewards(db, winner, loser, bet_coins)
    
    combat = Combat(
        challenger_id=challenger.id,
        defender_id=defender.id,
        winner_id=result.winner_id,
        bet_coins=bet_coins,
        combat_log=result.combat_log,
        challenger_stats=challenger_stats.to_dict(),
        defender_stats=defender_stats.to_dict(),
        challenger_final_hp=result.challenger_final_hp,
        defender_final_hp=result.defender_final_hp,
        total_turns=result.total_turns,
        winner_xp_reward=rewards.get("winner", {}).get("xp_earned", 0),
        winner_coins_reward=rewards.get("winner", {}).get("coins_earned", 0),
        status="completed",
    )
    
    db.add(combat)
    return combat


def get_combat_preview(challenger: "User", defender: "User") -> dict:
    """
    Génère un aperçu du combat avant engagement.
    
    Args:
        challenger: Le challenger
        defender: Le défenseur
        
    Returns:
        Dict avec stats comparées et chances estimées
    """
    c_stats = get_combat_stats(challenger)
    d_stats = get_combat_stats(defender)
    
    # Estimation simple des chances (basée sur combat power)
    c_power = (c_stats.strength * 2 + c_stats.endurance * 1.5 + 
               c_stats.agility * 1.5 + c_stats.intelligence)
    d_power = (d_stats.strength * 2 + d_stats.endurance * 1.5 + 
               d_stats.agility * 1.5 + d_stats.intelligence)
    
    total_power = c_power + d_power
    c_win_chance = (c_power / total_power) if total_power > 0 else 0.5
    
    return {
        "challenger": {
            "username": challenger.username,
            "level": challenger.level,
            "hp": c_stats.max_hp,
            "strength": c_stats.strength,
            "endurance": c_stats.endurance,
            "agility": c_stats.agility,
            "intelligence": c_stats.intelligence,
            "dodge_chance": round(calculate_dodge_chance(c_stats.agility) * 100, 1),
            "crit_chance": round(calculate_crit_chance(c_stats.intelligence) * 100, 1),
        },
        "defender": {
            "username": defender.username,
            "level": defender.level,
            "hp": d_stats.max_hp,
            "strength": d_stats.strength,
            "endurance": d_stats.endurance,
            "agility": d_stats.agility,
            "intelligence": d_stats.intelligence,
            "dodge_chance": round(calculate_dodge_chance(d_stats.agility) * 100, 1),
            "crit_chance": round(calculate_crit_chance(d_stats.intelligence) * 100, 1),
        },
        "estimated_win_chance": {
            "challenger": round(c_win_chance * 100, 1),
            "defender": round((1 - c_win_chance) * 100, 1),
        },
    }


# =============================================================================
# CombatService Class (wrapper for router compatibility)
# =============================================================================

@dataclass
class CombatantState:
    """État d'un combattant pour la simulation."""
    user_id: UUID
    username: str
    character_name: str
    character_class: str
    level: int
    max_hp: int
    current_hp: int
    strength: int
    endurance: int
    agility: int
    intelligence: int
    weapon_bonus: int = 0
    armor_bonus: int = 0
    
    def to_stats_dict(self) -> dict:
        """Convert to stats dict for storage."""
        return {
            "user_id": str(self.user_id),
            "username": self.username,
            "name": self.character_name,
            "class": self.character_class,
            "level": self.level,
            "max_hp": self.max_hp,
            "strength": self.strength,
            "endurance": self.endurance,
            "agility": self.agility,
            "intelligence": self.intelligence,
        }


@dataclass
class CombatSimulationResult:
    """Résultat complet d'une simulation de combat."""
    winner_id: Optional[UUID]
    is_draw: bool
    challenger_stats: dict
    defender_stats: dict
    challenger_final_hp: int
    defender_final_hp: int
    total_turns: int
    combat_log: list = field(default_factory=list)
    winner_xp: int = 0
    winner_coins: int = 0
    summary: str = ""


class CombatService:
    """Service de combat PvP - wrapper class."""
    
    @staticmethod
    def create_combatant(character, equipment_bonuses: dict) -> CombatantState:
        """Crée l'état initial d'un combattant."""
        strength = character.strength + equipment_bonuses.get("strength", 0)
        endurance = character.endurance + equipment_bonuses.get("endurance", 0)
        agility = character.agility + equipment_bonuses.get("agility", 0)
        intelligence = character.intelligence + equipment_bonuses.get("intelligence", 0)
        
        max_hp = BASE_HP + (endurance * HP_PER_ENDURANCE)
        
        return CombatantState(
            user_id=character.user_id,
            username=character.user.username if character.user else "Unknown",
            character_name=character.name,
            character_class=character.character_class,
            level=character.user.level if character.user else 1,
            max_hp=max_hp,
            current_hp=max_hp,
            strength=strength,
            endurance=endurance,
            agility=agility,
            intelligence=intelligence,
        )
    
    @staticmethod
    def simulate_combat(
        challenger: CombatantState,
        defender: CombatantState,
        bet_coins: int = 0
    ) -> CombatSimulationResult:
        """Simule un combat complet."""
        combat_log = []
        turn = 0
        attacker_first = challenger.agility >= defender.agility
        
        while turn < MAX_TURNS:
            turn += 1
            
            # Challenger attacks
            if attacker_first or turn > 1:
                damage, is_crit, is_dodged = calculate_damage(
                    CombatStats(
                        challenger.user_id, challenger.username,
                        challenger.max_hp, challenger.current_hp,
                        challenger.strength, challenger.endurance,
                        challenger.agility, challenger.intelligence,
                        challenger.weapon_bonus, challenger.armor_bonus
                    ),
                    CombatStats(
                        defender.user_id, defender.username,
                        defender.max_hp, defender.current_hp,
                        defender.strength, defender.endurance,
                        defender.agility, defender.intelligence,
                        defender.weapon_bonus, defender.armor_bonus
                    )
                )
                
                if not is_dodged:
                    defender.current_hp -= damage
                
                combat_log.append({
                    "turn": turn,
                    "attacker_id": str(challenger.user_id),
                    "defender_id": str(defender.user_id),
                    "action": "attack",
                    "damage_dealt": damage if not is_dodged else 0,
                    "is_critical": is_crit,
                    "is_dodge": is_dodged,
                    "attacker_hp": challenger.current_hp,
                    "defender_hp": max(0, defender.current_hp),
                    "message": f"{challenger.username} " + (
                        f"esquivé par {defender.username}" if is_dodged else
                        f"CRITIQUE! {damage} dégâts" if is_crit else
                        f"inflige {damage} dégâts"
                    ),
                })
                
                if defender.current_hp <= 0:
                    break
            
            # Defender attacks
            damage, is_crit, is_dodged = calculate_damage(
                CombatStats(
                    defender.user_id, defender.username,
                    defender.max_hp, defender.current_hp,
                    defender.strength, defender.endurance,
                    defender.agility, defender.intelligence,
                    defender.weapon_bonus, defender.armor_bonus
                ),
                CombatStats(
                    challenger.user_id, challenger.username,
                    challenger.max_hp, challenger.current_hp,
                    challenger.strength, challenger.endurance,
                    challenger.agility, challenger.intelligence,
                    challenger.weapon_bonus, challenger.armor_bonus
                )
            )
            
            if not is_dodged:
                challenger.current_hp -= damage
            
            combat_log.append({
                "turn": turn,
                "attacker_id": str(defender.user_id),
                "defender_id": str(challenger.user_id),
                "action": "attack",
                "damage_dealt": damage if not is_dodged else 0,
                "is_critical": is_crit,
                "is_dodge": is_dodged,
                "attacker_hp": defender.current_hp,
                "defender_hp": max(0, challenger.current_hp),
                "message": f"{defender.username} " + (
                    f"esquivé par {challenger.username}" if is_dodged else
                    f"CRITIQUE! {damage} dégâts" if is_crit else
                    f"inflige {damage} dégâts"
                ),
            })
            
            if challenger.current_hp <= 0:
                break
            
            attacker_first = True
        
        # Determine winner
        winner_id = None
        is_draw = False
        
        if challenger.current_hp <= 0 and defender.current_hp <= 0:
            is_draw = True
        elif defender.current_hp <= 0:
            winner_id = challenger.user_id
        elif challenger.current_hp <= 0:
            winner_id = defender.user_id
        else:
            c_pct = challenger.current_hp / challenger.max_hp
            d_pct = defender.current_hp / defender.max_hp
            if c_pct > d_pct:
                winner_id = challenger.user_id
            elif d_pct > c_pct:
                winner_id = defender.user_id
            else:
                is_draw = True
        
        # Calculate rewards
        winner_xp = BASE_XP_WIN if winner_id else 0
        winner_coins = (BASE_COINS_WIN + bet_coins) if winner_id else 0
        
        if is_draw:
            summary = "Match nul !"
        elif winner_id == challenger.user_id:
            summary = f"{challenger.username} gagne en {turn} tours !"
        else:
            summary = f"{defender.username} gagne en {turn} tours !"
        
        return CombatSimulationResult(
            winner_id=winner_id,
            is_draw=is_draw,
            challenger_stats=challenger.to_stats_dict(),
            defender_stats=defender.to_stats_dict(),
            challenger_final_hp=max(0, challenger.current_hp),
            defender_final_hp=max(0, defender.current_hp),
            total_turns=turn,
            combat_log=combat_log,
            winner_xp=winner_xp,
            winner_coins=winner_coins,
            summary=summary,
        )
