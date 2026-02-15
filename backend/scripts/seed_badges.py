#!/usr/bin/env python3
"""
Seed badges into the database.
Reads from badges_wtf.sql or uses Python definitions.
"""
import asyncio
import os
import sys
from uuid import uuid4

# Add app to path
sys.path.insert(0, "/app")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://habit_user:password@postgres:5432/habit_tracker"
)

# Badge definitions
BADGES = [
    # === STREAK BADGES ===
    {"code": "streak_week", "name": "Une Semaine", "description": "7 jours de streak", "icon": "🔥", "rarity": "common", "xp_reward": 25, "condition_type": "streak", "condition_value": '{"min_streak": 7}'},
    {"code": "streak_2weeks", "name": "Deux Semaines", "description": "14 jours de streak", "icon": "🔥", "rarity": "uncommon", "xp_reward": 50, "condition_type": "streak", "condition_value": '{"min_streak": 14}'},
    {"code": "streak_month", "name": "Un Mois", "description": "30 jours de streak", "icon": "🔥", "rarity": "rare", "xp_reward": 100, "condition_type": "streak", "condition_value": '{"min_streak": 30}'},
    {"code": "streak_2months", "name": "Deux Mois", "description": "60 jours de streak", "icon": "🔥", "rarity": "epic", "xp_reward": 200, "condition_type": "streak", "condition_value": '{"min_streak": 60}'},
    {"code": "streak_quarter", "name": "Un Trimestre", "description": "90 jours de streak", "icon": "🔥", "rarity": "epic", "xp_reward": 300, "condition_type": "streak", "condition_value": '{"min_streak": 90}'},
    {"code": "streak_half", "name": "Six Mois", "description": "180 jours de streak", "icon": "🔥", "rarity": "legendary", "xp_reward": 500, "condition_type": "streak", "condition_value": '{"min_streak": 180}'},
    {"code": "streak_year", "name": "Une Année", "description": "365 jours de streak", "icon": "👑", "rarity": "legendary", "xp_reward": 1000, "condition_type": "streak", "condition_value": '{"min_streak": 365}'},
    
    # === COMPLETION BADGES ===
    {"code": "first_habit", "name": "Premier Pas", "description": "Compléter ta première habitude", "icon": "🎯", "rarity": "common", "xp_reward": 10, "condition_type": "completions", "condition_value": '{"count": 1}'},
    {"code": "completions_10", "name": "Débutant", "description": "10 habitudes complétées", "icon": "⭐", "rarity": "common", "xp_reward": 25, "condition_type": "completions", "condition_value": '{"count": 10}'},
    {"code": "completions_50", "name": "Régulier", "description": "50 habitudes complétées", "icon": "⭐", "rarity": "uncommon", "xp_reward": 50, "condition_type": "completions", "condition_value": '{"count": 50}'},
    {"code": "completions_100", "name": "Assidu", "description": "100 habitudes complétées", "icon": "⭐", "rarity": "rare", "xp_reward": 100, "condition_type": "completions", "condition_value": '{"count": 100}'},
    {"code": "completions_500", "name": "Expert", "description": "500 habitudes complétées", "icon": "💎", "rarity": "epic", "xp_reward": 250, "condition_type": "completions", "condition_value": '{"count": 500}'},
    {"code": "completions_1000", "name": "Maître", "description": "1000 habitudes complétées", "icon": "👑", "rarity": "legendary", "xp_reward": 500, "condition_type": "completions", "condition_value": '{"count": 1000}'},
    
    # === LEVEL BADGES ===
    {"code": "level_5", "name": "Niveau 5", "description": "Atteindre le niveau 5", "icon": "📈", "rarity": "common", "xp_reward": 25, "condition_type": "level", "condition_value": '{"min_level": 5}'},
    {"code": "level_10", "name": "Niveau 10", "description": "Atteindre le niveau 10", "icon": "📈", "rarity": "uncommon", "xp_reward": 50, "condition_type": "level", "condition_value": '{"min_level": 10}'},
    {"code": "level_25", "name": "Niveau 25", "description": "Atteindre le niveau 25", "icon": "📈", "rarity": "rare", "xp_reward": 100, "condition_type": "level", "condition_value": '{"min_level": 25}'},
    {"code": "level_50", "name": "Niveau 50", "description": "Atteindre le niveau 50", "icon": "🏆", "rarity": "epic", "xp_reward": 250, "condition_type": "level", "condition_value": '{"min_level": 50}'},
    {"code": "level_100", "name": "Niveau 100", "description": "Atteindre le niveau 100", "icon": "👑", "rarity": "legendary", "xp_reward": 500, "condition_type": "level", "condition_value": '{"min_level": 100}'},
    
    # === FUN BADGES ===
    {"code": "early_bird", "name": "Lève-Tôt", "description": "Compléter une habitude avant 6h du matin", "icon": "🐦", "rarity": "uncommon", "xp_reward": 50, "condition_type": "time_based", "condition_value": '{"before_hour": 6}'},
    {"code": "night_owl", "name": "Oiseau de Nuit", "description": "Compléter une habitude après 23h", "icon": "🦉", "rarity": "uncommon", "xp_reward": 50, "condition_type": "time_based", "condition_value": '{"after_hour": 23}'},
    {"code": "weekend_warrior", "name": "Guerrier du Weekend", "description": "Compléter des habitudes samedi et dimanche", "icon": "⚔️", "rarity": "uncommon", "xp_reward": 50, "condition_type": "day_completions", "condition_value": '{"days": ["saturday", "sunday"]}'},
    {"code": "shopaholic", "name": "Accro au Shopping", "description": "Acheter 10 items dans la boutique", "icon": "🛍️", "rarity": "rare", "xp_reward": 100, "condition_type": "purchases", "condition_value": '{"count": 10}'},
    {"code": "social_butterfly", "name": "Papillon Social", "description": "Avoir 10 amis", "icon": "🦋", "rarity": "rare", "xp_reward": 100, "condition_type": "friends", "condition_value": '{"count": 10}'},
]


async def seed_badges():
    """Seed badges into database."""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check existing badges
        result = await session.execute(text("SELECT code FROM badges"))
        existing_codes = {row[0] for row in result.fetchall()}
        
        inserted = 0
        for badge in BADGES:
            if badge["code"] in existing_codes:
                print(f"  Skip: {badge['code']} (exists)")
                continue
                
            await session.execute(
                text("""
                    INSERT INTO badges (id, code, name, description, icon, rarity, xp_reward, condition_type, condition_value, is_secret, is_seasonal)
                    VALUES (:id, :code, :name, :description, :icon, :rarity, :xp_reward, :condition_type, :condition_value, false, false)
                """),
                {
                    "id": str(uuid4()),
                    "code": badge["code"],
                    "name": badge["name"],
                    "description": badge["description"],
                    "icon": badge["icon"],
                    "rarity": badge["rarity"],
                    "xp_reward": badge["xp_reward"],
                    "condition_type": badge["condition_type"],
                    "condition_value": badge["condition_value"],
                }
            )
            inserted += 1
            print(f"  Added: {badge['code']}")
        
        await session.commit()
        print(f"\nSeeded {inserted} new badges (skipped {len(existing_codes)} existing)")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🏆 Seeding badges...")
    asyncio.run(seed_badges())
    print("✅ Done!")
