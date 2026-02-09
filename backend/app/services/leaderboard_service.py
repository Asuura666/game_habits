"""
Leaderboard Service - Classements avec Redis.

Utilise Redis Sorted Sets pour des classements performants:
- ZADD pour ajouter/mettre à jour les scores
- ZREVRANK pour obtenir le rang
- ZREVRANGE pour les top N
- ZRANGEBYSCORE pour filtrer par score

Types de classements:
- xp_daily: XP gagné aujourd'hui
- xp_weekly: XP gagné cette semaine
- xp_monthly: XP gagné ce mois
- xp_alltime: XP total
- streak: Meilleur streak actuel
- combat_wins: Victoires PvP
"""
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.user import User

# Configuration Redis
REDIS_URL = "redis://localhost:6379"
LEADERBOARD_PREFIX = "habit:leaderboard"

# Périodes
PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
PERIOD_ALLTIME = "alltime"

# Types de classements
TYPE_XP = "xp"
TYPE_STREAK = "streak"
TYPE_COMBAT = "combat"


def _get_redis_key(leaderboard_type: str, period: str, date_suffix: str = "") -> str:
    """Génère la clé Redis pour un classement."""
    if date_suffix:
        return f"{LEADERBOARD_PREFIX}:{leaderboard_type}:{period}:{date_suffix}"
    return f"{LEADERBOARD_PREFIX}:{leaderboard_type}:{period}"


def _get_period_suffix(period: str) -> str:
    """Génère le suffixe de date pour la période."""
    today = date.today()
    
    if period == PERIOD_DAILY:
        return today.isoformat()
    elif period == PERIOD_WEEKLY:
        # ISO week
        return f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"
    elif period == PERIOD_MONTHLY:
        return f"{today.year}-{today.month:02d}"
    else:
        return ""


async def get_redis_client() -> redis.Redis:
    """Crée et retourne un client Redis."""
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def update_xp_leaderboard(
    user_id: UUID,
    xp_gained: int,
    username: str = ""
) -> None:
    """
    Met à jour les classements XP pour un utilisateur.
    
    Incrémente le score dans tous les classements XP pertinents.
    
    Args:
        user_id: ID de l'utilisateur
        xp_gained: XP gagné à ajouter
        username: Nom d'utilisateur (pour stockage)
    """
    client = await get_redis_client()
    user_key = str(user_id)
    
    try:
        # Mettre à jour chaque période
        for period in [PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_ALLTIME]:
            suffix = _get_period_suffix(period)
            key = _get_redis_key(TYPE_XP, period, suffix)
            
            # ZINCRBY: incrémente le score (crée l'entrée si inexistante)
            await client.zincrby(key, xp_gained, user_key)
        
        # Stocker le username pour affichage
        await client.hset(f"{LEADERBOARD_PREFIX}:usernames", user_key, username)
        
        # Définir TTL pour les classements temporaires
        daily_key = _get_redis_key(TYPE_XP, PERIOD_DAILY, _get_period_suffix(PERIOD_DAILY))
        await client.expire(daily_key, 86400 * 2)  # 2 jours
        
        weekly_key = _get_redis_key(TYPE_XP, PERIOD_WEEKLY, _get_period_suffix(PERIOD_WEEKLY))
        await client.expire(weekly_key, 86400 * 14)  # 2 semaines
        
    finally:
        await client.close()


async def update_streak_leaderboard(
    user_id: UUID,
    streak: int,
    username: str = ""
) -> None:
    """
    Met à jour le classement des streaks.
    
    Remplace le score (pas d'incrément car c'est le streak actuel).
    
    Args:
        user_id: ID de l'utilisateur
        streak: Streak actuel
        username: Nom d'utilisateur
    """
    client = await get_redis_client()
    user_key = str(user_id)
    
    try:
        key = _get_redis_key(TYPE_STREAK, PERIOD_ALLTIME)
        await client.zadd(key, {user_key: streak})
        
        if username:
            await client.hset(f"{LEADERBOARD_PREFIX}:usernames", user_key, username)
    finally:
        await client.close()


async def update_combat_leaderboard(
    user_id: UUID,
    wins_delta: int = 1,
    username: str = ""
) -> None:
    """
    Met à jour le classement des victoires en combat.
    
    Args:
        user_id: ID de l'utilisateur
        wins_delta: Nombre de victoires à ajouter (généralement 1)
        username: Nom d'utilisateur
    """
    client = await get_redis_client()
    user_key = str(user_id)
    
    try:
        for period in [PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_ALLTIME]:
            suffix = _get_period_suffix(period)
            key = _get_redis_key(TYPE_COMBAT, period, suffix)
            await client.zincrby(key, wins_delta, user_key)
        
        if username:
            await client.hset(f"{LEADERBOARD_PREFIX}:usernames", user_key, username)
    finally:
        await client.close()


async def get_leaderboard(
    leaderboard_type: str,
    period: str,
    limit: int = 10,
    offset: int = 0
) -> list[dict]:
    """
    Récupère un classement.
    
    Args:
        leaderboard_type: Type (xp, streak, combat)
        period: Période (daily, weekly, monthly, alltime)
        limit: Nombre d'entrées
        offset: Décalage (pour pagination)
        
    Returns:
        Liste de dicts avec rank, user_id, username, score
    """
    client = await get_redis_client()
    
    try:
        suffix = _get_period_suffix(period)
        key = _get_redis_key(leaderboard_type, period, suffix)
        
        # ZREVRANGE avec scores (ordre décroissant)
        results = await client.zrevrange(key, offset, offset + limit - 1, withscores=True)
        
        # Récupérer les usernames
        usernames = await client.hgetall(f"{LEADERBOARD_PREFIX}:usernames")
        
        leaderboard = []
        for rank, (user_id, score) in enumerate(results, start=offset + 1):
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "username": usernames.get(user_id, "Unknown"),
                "score": int(score),
            })
        
        return leaderboard
    finally:
        await client.close()


async def get_friends_leaderboard(
    db: Session,
    user: "User",
    leaderboard_type: str,
    period: str
) -> list[dict]:
    """
    Récupère le classement filtré aux amis de l'utilisateur.
    
    Args:
        db: Session de base de données
        user: L'utilisateur
        leaderboard_type: Type de classement
        period: Période
        
    Returns:
        Liste triée des amis avec leurs scores
    """
    from app.models.friendship import Friendship
    
    # Récupérer les IDs des amis
    friendships = db.query(Friendship).filter(
        ((Friendship.requester_id == user.id) | (Friendship.addressee_id == user.id)),
        Friendship.status == "accepted"
    ).all()
    
    friend_ids = set()
    for f in friendships:
        if f.requester_id == user.id:
            friend_ids.add(str(f.addressee_id))
        else:
            friend_ids.add(str(f.requester_id))
    
    # Ajouter l'utilisateur lui-même
    friend_ids.add(str(user.id))
    
    client = await get_redis_client()
    
    try:
        suffix = _get_period_suffix(period)
        key = _get_redis_key(leaderboard_type, period, suffix)
        
        # Récupérer les scores pour chaque ami
        scores = []
        for user_id in friend_ids:
            score = await client.zscore(key, user_id)
            if score is not None:
                scores.append((user_id, score))
        
        # Trier par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Récupérer les usernames
        usernames = await client.hgetall(f"{LEADERBOARD_PREFIX}:usernames")
        
        leaderboard = []
        for rank, (user_id, score) in enumerate(scores, start=1):
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "username": usernames.get(user_id, "Unknown"),
                "score": int(score),
                "is_self": user_id == str(user.id),
            })
        
        return leaderboard
    finally:
        await client.close()


async def get_user_rank(
    user_id: UUID,
    leaderboard_type: str,
    period: str
) -> dict:
    """
    Récupère le rang et score d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        leaderboard_type: Type de classement
        period: Période
        
    Returns:
        Dict avec rank, score, total_players
    """
    client = await get_redis_client()
    user_key = str(user_id)
    
    try:
        suffix = _get_period_suffix(period)
        key = _get_redis_key(leaderboard_type, period, suffix)
        
        # ZREVRANK: rang (0-indexed, donc +1)
        rank = await client.zrevrank(key, user_key)
        score = await client.zscore(key, user_key)
        total = await client.zcard(key)
        
        if rank is None:
            return {
                "rank": None,
                "score": 0,
                "total_players": total,
            }
        
        return {
            "rank": rank + 1,
            "score": int(score) if score else 0,
            "total_players": total,
        }
    finally:
        await client.close()


async def check_rank_change(
    user_id: UUID,
    leaderboard_key: str
) -> dict:
    """
    Vérifie si le rang de l'utilisateur a changé.
    
    Utilise un hash Redis pour stocker le dernier rang connu.
    
    Args:
        user_id: ID de l'utilisateur
        leaderboard_key: Clé du classement à vérifier
        
    Returns:
        Dict avec old_rank, new_rank, improved (bool)
    """
    client = await get_redis_client()
    user_key = str(user_id)
    rank_history_key = f"{leaderboard_key}:rank_history"
    
    try:
        # Récupérer le rang actuel
        new_rank = await client.zrevrank(leaderboard_key, user_key)
        if new_rank is not None:
            new_rank += 1
        
        # Récupérer l'ancien rang
        old_rank_str = await client.hget(rank_history_key, user_key)
        old_rank = int(old_rank_str) if old_rank_str else None
        
        # Sauvegarder le nouveau rang
        if new_rank is not None:
            await client.hset(rank_history_key, user_key, str(new_rank))
        
        # Analyser le changement
        improved = False
        if old_rank is not None and new_rank is not None:
            improved = new_rank < old_rank  # Plus petit rang = meilleur
        
        return {
            "old_rank": old_rank,
            "new_rank": new_rank,
            "improved": improved,
            "rank_change": (old_rank - new_rank) if (old_rank and new_rank) else 0,
        }
    finally:
        await client.close()


async def get_top_around_user(
    user_id: UUID,
    leaderboard_type: str,
    period: str,
    around: int = 2
) -> list[dict]:
    """
    Récupère les joueurs autour de l'utilisateur dans le classement.
    
    Retourne [around] joueurs au-dessus et [around] en-dessous.
    
    Args:
        user_id: ID de l'utilisateur
        leaderboard_type: Type de classement
        period: Période
        around: Nombre de joueurs de chaque côté
        
    Returns:
        Liste triée avec l'utilisateur au milieu
    """
    client = await get_redis_client()
    user_key = str(user_id)
    
    try:
        suffix = _get_period_suffix(period)
        key = _get_redis_key(leaderboard_type, period, suffix)
        
        rank = await client.zrevrank(key, user_key)
        if rank is None:
            return []
        
        # Calculer la fenêtre
        start = max(0, rank - around)
        end = rank + around
        
        results = await client.zrevrange(key, start, end, withscores=True)
        usernames = await client.hgetall(f"{LEADERBOARD_PREFIX}:usernames")
        
        leaderboard = []
        for idx, (uid, score) in enumerate(results):
            leaderboard.append({
                "rank": start + idx + 1,
                "user_id": uid,
                "username": usernames.get(uid, "Unknown"),
                "score": int(score),
                "is_self": uid == user_key,
            })
        
        return leaderboard
    finally:
        await client.close()


async def cleanup_old_leaderboards(days_to_keep: int = 30) -> int:
    """
    Nettoie les anciens classements expirés.
    
    Args:
        days_to_keep: Nombre de jours à conserver
        
    Returns:
        Nombre de clés supprimées
    """
    client = await get_redis_client()
    deleted = 0
    
    try:
        # Récupérer toutes les clés de leaderboard
        keys = await client.keys(f"{LEADERBOARD_PREFIX}:*")
        
        cutoff = date.today() - timedelta(days=days_to_keep)
        
        for key in keys:
            # Parser la date du suffixe si présent
            parts = key.split(":")
            if len(parts) >= 4:
                date_suffix = parts[-1]
                try:
                    if "-W" in date_suffix:
                        # Format semaine (2024-W01)
                        continue  # Skip, complexe à parser
                    else:
                        # Format jour (2024-01-15) ou mois (2024-01)
                        key_date = datetime.strptime(date_suffix[:10], "%Y-%m-%d").date()
                        if key_date < cutoff:
                            await client.delete(key)
                            deleted += 1
                except ValueError:
                    continue
        
        return deleted
    finally:
        await client.close()
