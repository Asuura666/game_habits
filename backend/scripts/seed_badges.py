#!/usr/bin/env python3
"""
Seed badges into the database.
Complete badge collection for HabitQuest (75 badges).

Categories:
- streak: Consecutive days
- completions: Total habits completed
- level: Level reached
- time_based: Time of day completions
- combat_wins: PvP victories
- date: Seasonal/special dates
- coins: Gold accumulated
- habit_category: Category-specific completions
- friends: Social achievements
- secret: Hidden achievements
- purchases: Shop activity

Run with: docker compose exec backend python scripts/seed_badges.py
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

# Complete Badge Collection (75 badges)
BADGES = [
    # =============================================================================
    # STREAK BADGES (7)
    # =============================================================================
    {"code": "streak_week", "name": "Une Semaine", "description": "7 jours de streak", "icon": "🔥", "rarity": "common", "xp_reward": 25, "condition_type": "streak", "condition_value": '{"min_streak": 7}'},
    {"code": "streak_2weeks", "name": "Deux Semaines", "description": "14 jours de streak", "icon": "🔥", "rarity": "uncommon", "xp_reward": 50, "condition_type": "streak", "condition_value": '{"min_streak": 14}'},
    {"code": "streak_month", "name": "Un Mois", "description": "30 jours de streak", "icon": "🔥", "rarity": "rare", "xp_reward": 100, "condition_type": "streak", "condition_value": '{"min_streak": 30}'},
    {"code": "streak_2months", "name": "Deux Mois", "description": "60 jours de streak", "icon": "🔥", "rarity": "epic", "xp_reward": 200, "condition_type": "streak", "condition_value": '{"min_streak": 60}'},
    {"code": "streak_quarter", "name": "Un Trimestre", "description": "90 jours de streak", "icon": "🔥", "rarity": "epic", "xp_reward": 300, "condition_type": "streak", "condition_value": '{"min_streak": 90}'},
    {"code": "streak_half", "name": "Six Mois", "description": "180 jours de streak", "icon": "🔥", "rarity": "legendary", "xp_reward": 500, "condition_type": "streak", "condition_value": '{"min_streak": 180}'},
    {"code": "streak_year", "name": "Une Année", "description": "365 jours de streak - L'ultime accomplissement", "icon": "👑", "rarity": "legendary", "xp_reward": 1000, "condition_type": "streak", "condition_value": '{"min_streak": 365}'},
    
    # =============================================================================
    # COMPLETION BADGES (10)
    # =============================================================================
    {"code": "first_habit", "name": "Premier Pas", "description": "Compléter ta première habitude", "icon": "🎯", "rarity": "common", "xp_reward": 10, "condition_type": "completions", "condition_value": '{"min_completions": 1}'},
    {"code": "completions_10", "name": "Débutant", "description": "10 habitudes complétées", "icon": "⭐", "rarity": "common", "xp_reward": 25, "condition_type": "completions", "condition_value": '{"min_completions": 10}'},
    {"code": "completions_25", "name": "Apprenti", "description": "25 habitudes complétées", "icon": "⭐", "rarity": "common", "xp_reward": 35, "condition_type": "completions", "condition_value": '{"min_completions": 25}'},
    {"code": "completions_50", "name": "Régulier", "description": "50 habitudes complétées", "icon": "⭐", "rarity": "uncommon", "xp_reward": 50, "condition_type": "completions", "condition_value": '{"min_completions": 50}'},
    {"code": "completions_100", "name": "Assidu", "description": "100 habitudes complétées", "icon": "⭐", "rarity": "rare", "xp_reward": 100, "condition_type": "completions", "condition_value": '{"min_completions": 100}'},
    {"code": "completions_250", "name": "Dévoué", "description": "250 habitudes complétées", "icon": "💫", "rarity": "rare", "xp_reward": 150, "condition_type": "completions", "condition_value": '{"min_completions": 250}'},
    {"code": "completions_500", "name": "Expert", "description": "500 habitudes complétées", "icon": "💎", "rarity": "epic", "xp_reward": 250, "condition_type": "completions", "condition_value": '{"min_completions": 500}'},
    {"code": "completions_750", "name": "Vétéran", "description": "750 habitudes complétées", "icon": "💎", "rarity": "epic", "xp_reward": 350, "condition_type": "completions", "condition_value": '{"min_completions": 750}'},
    {"code": "completions_1000", "name": "Maître", "description": "1000 habitudes complétées", "icon": "👑", "rarity": "legendary", "xp_reward": 500, "condition_type": "completions", "condition_value": '{"min_completions": 1000}'},
    {"code": "completions_2000", "name": "Légende", "description": "2000 habitudes complétées - Tu es une légende", "icon": "🏆", "rarity": "legendary", "xp_reward": 1000, "condition_type": "completions", "condition_value": '{"min_completions": 2000}'},
    
    # =============================================================================
    # LEVEL BADGES (10)
    # =============================================================================
    {"code": "level_5", "name": "Niveau 5", "description": "Atteindre le niveau 5", "icon": "📈", "rarity": "common", "xp_reward": 25, "condition_type": "level", "condition_value": '{"min_level": 5}'},
    {"code": "level_10", "name": "Niveau 10", "description": "Atteindre le niveau 10", "icon": "📈", "rarity": "uncommon", "xp_reward": 50, "condition_type": "level", "condition_value": '{"min_level": 10}'},
    {"code": "level_15", "name": "Niveau 15", "description": "Atteindre le niveau 15", "icon": "📈", "rarity": "uncommon", "xp_reward": 75, "condition_type": "level", "condition_value": '{"min_level": 15}'},
    {"code": "level_20", "name": "Niveau 20", "description": "Atteindre le niveau 20", "icon": "📈", "rarity": "rare", "xp_reward": 100, "condition_type": "level", "condition_value": '{"min_level": 20}'},
    {"code": "level_25", "name": "Niveau 25", "description": "Atteindre le niveau 25", "icon": "📈", "rarity": "rare", "xp_reward": 125, "condition_type": "level", "condition_value": '{"min_level": 25}'},
    {"code": "level_30", "name": "Niveau 30", "description": "Atteindre le niveau 30", "icon": "🏆", "rarity": "rare", "xp_reward": 150, "condition_type": "level", "condition_value": '{"min_level": 30}'},
    {"code": "level_40", "name": "Niveau 40", "description": "Atteindre le niveau 40", "icon": "🏆", "rarity": "epic", "xp_reward": 200, "condition_type": "level", "condition_value": '{"min_level": 40}'},
    {"code": "level_50", "name": "Niveau 50", "description": "Atteindre le niveau 50", "icon": "🏆", "rarity": "epic", "xp_reward": 250, "condition_type": "level", "condition_value": '{"min_level": 50}'},
    {"code": "level_75", "name": "Niveau 75", "description": "Atteindre le niveau 75", "icon": "👑", "rarity": "legendary", "xp_reward": 400, "condition_type": "level", "condition_value": '{"min_level": 75}'},
    {"code": "level_100", "name": "Niveau 100", "description": "Atteindre le niveau 100 - Maître Ultime", "icon": "👑", "rarity": "legendary", "xp_reward": 500, "condition_type": "level", "condition_value": '{"min_level": 100}'},
    
    # =============================================================================
    # TIME-BASED BADGES (6)
    # =============================================================================
    {"code": "early_bird", "name": "Lève-Tôt", "description": "Compléter une habitude avant 6h du matin", "icon": "🐦", "rarity": "uncommon", "xp_reward": 50, "condition_type": "time", "condition_value": '{"time_type": "early_bird", "count": 1}'},
    {"code": "early_bird_10", "name": "Matinal Confirmé", "description": "10 habitudes avant 6h du matin", "icon": "🌅", "rarity": "rare", "xp_reward": 100, "condition_type": "time", "condition_value": '{"time_type": "early_bird", "count": 10}'},
    {"code": "night_owl", "name": "Oiseau de Nuit", "description": "Compléter une habitude après 23h", "icon": "🦉", "rarity": "uncommon", "xp_reward": 50, "condition_type": "time", "condition_value": '{"time_type": "night_owl", "count": 1}'},
    {"code": "night_owl_10", "name": "Noctambule", "description": "10 habitudes après 23h", "icon": "🌙", "rarity": "rare", "xp_reward": 100, "condition_type": "time", "condition_value": '{"time_type": "night_owl", "count": 10}'},
    {"code": "weekend_warrior", "name": "Guerrier du Weekend", "description": "Compléter des habitudes samedi et dimanche", "icon": "⚔️", "rarity": "uncommon", "xp_reward": 50, "condition_type": "day_completions", "condition_value": '{"days": ["saturday", "sunday"]}'},
    {"code": "lunch_break", "name": "Pause Productive", "description": "5 habitudes entre 12h et 14h", "icon": "🍽️", "rarity": "uncommon", "xp_reward": 40, "condition_type": "time", "condition_value": '{"time_type": "lunch", "count": 5}'},
    
    # =============================================================================
    # COMBAT/PVP BADGES (8)
    # =============================================================================
    {"code": "first_victory", "name": "Première Victoire", "description": "Gagner ton premier combat", "icon": "⚔️", "rarity": "common", "xp_reward": 25, "condition_type": "combat_wins", "condition_value": '{"min_wins": 1}'},
    {"code": "wins_5", "name": "Combattant", "description": "Gagner 5 combats", "icon": "⚔️", "rarity": "uncommon", "xp_reward": 50, "condition_type": "combat_wins", "condition_value": '{"min_wins": 5}'},
    {"code": "wins_10", "name": "Duelliste", "description": "Gagner 10 combats", "icon": "🗡️", "rarity": "rare", "xp_reward": 100, "condition_type": "combat_wins", "condition_value": '{"min_wins": 10}'},
    {"code": "wins_25", "name": "Gladiateur", "description": "Gagner 25 combats", "icon": "🗡️", "rarity": "rare", "xp_reward": 150, "condition_type": "combat_wins", "condition_value": '{"min_wins": 25}'},
    {"code": "wins_50", "name": "Champion", "description": "Gagner 50 combats", "icon": "🏆", "rarity": "epic", "xp_reward": 250, "condition_type": "combat_wins", "condition_value": '{"min_wins": 50}'},
    {"code": "wins_100", "name": "Invincible", "description": "Gagner 100 combats", "icon": "👑", "rarity": "legendary", "xp_reward": 500, "condition_type": "combat_wins", "condition_value": '{"min_wins": 100}'},
    {"code": "win_streak_3", "name": "Série de Victoires", "description": "3 victoires consécutives", "icon": "🔥", "rarity": "rare", "xp_reward": 75, "condition_type": "combat_wins", "condition_value": '{"win_streak": 3}'},
    {"code": "win_streak_5", "name": "Imbattable", "description": "5 victoires consécutives", "icon": "💥", "rarity": "epic", "xp_reward": 150, "condition_type": "combat_wins", "condition_value": '{"win_streak": 5}'},
    
    # =============================================================================
    # COIN/WEALTH BADGES (6)
    # =============================================================================
    {"code": "coins_100", "name": "Épargnant", "description": "Accumuler 100 pièces", "icon": "🪙", "rarity": "common", "xp_reward": 20, "condition_type": "coins", "condition_value": '{"min_coins": 100}'},
    {"code": "coins_500", "name": "Économe", "description": "Accumuler 500 pièces", "icon": "💰", "rarity": "uncommon", "xp_reward": 50, "condition_type": "coins", "condition_value": '{"min_coins": 500}'},
    {"code": "coins_1000", "name": "Riche", "description": "Accumuler 1000 pièces", "icon": "💰", "rarity": "rare", "xp_reward": 100, "condition_type": "coins", "condition_value": '{"min_coins": 1000}'},
    {"code": "coins_2500", "name": "Fortuné", "description": "Accumuler 2500 pièces", "icon": "💎", "rarity": "epic", "xp_reward": 200, "condition_type": "coins", "condition_value": '{"min_coins": 2500}'},
    {"code": "coins_5000", "name": "Millionnaire", "description": "Accumuler 5000 pièces", "icon": "👑", "rarity": "legendary", "xp_reward": 400, "condition_type": "coins", "condition_value": '{"min_coins": 5000}'},
    {"code": "coins_10000", "name": "Trésor Vivant", "description": "Accumuler 10000 pièces", "icon": "🏦", "rarity": "legendary", "xp_reward": 750, "condition_type": "coins", "condition_value": '{"min_coins": 10000}'},
    
    # =============================================================================
    # HABIT CATEGORY BADGES (8)
    # =============================================================================
    {"code": "health_master", "name": "Corps Sain", "description": "50 habitudes de santé complétées", "icon": "💪", "rarity": "rare", "xp_reward": 100, "condition_type": "habit_category", "condition_value": '{"category": "health", "min_completions": 50}'},
    {"code": "fitness_guru", "name": "Athlète", "description": "100 habitudes de fitness complétées", "icon": "🏃", "rarity": "epic", "xp_reward": 200, "condition_type": "habit_category", "condition_value": '{"category": "fitness", "min_completions": 100}'},
    {"code": "mindful_one", "name": "Esprit Zen", "description": "50 habitudes de bien-être mental complétées", "icon": "🧘", "rarity": "rare", "xp_reward": 100, "condition_type": "habit_category", "condition_value": '{"category": "mindfulness", "min_completions": 50}'},
    {"code": "bookworm", "name": "Rat de Bibliothèque", "description": "50 habitudes de lecture complétées", "icon": "📚", "rarity": "rare", "xp_reward": 100, "condition_type": "habit_category", "condition_value": '{"category": "learning", "min_completions": 50}'},
    {"code": "scholar", "name": "Érudit", "description": "100 habitudes d'apprentissage complétées", "icon": "🎓", "rarity": "epic", "xp_reward": 200, "condition_type": "habit_category", "condition_value": '{"category": "learning", "min_completions": 100}'},
    {"code": "productive", "name": "Productif", "description": "50 habitudes de productivité complétées", "icon": "⚡", "rarity": "rare", "xp_reward": 100, "condition_type": "habit_category", "condition_value": '{"category": "productivity", "min_completions": 50}'},
    {"code": "creative_soul", "name": "Âme Créative", "description": "50 habitudes créatives complétées", "icon": "🎨", "rarity": "rare", "xp_reward": 100, "condition_type": "habit_category", "condition_value": '{"category": "creativity", "min_completions": 50}'},
    {"code": "polyvalent", "name": "Polyvalent", "description": "Compléter des habitudes dans 5 catégories différentes", "icon": "🌈", "rarity": "epic", "xp_reward": 150, "condition_type": "habit_category", "condition_value": '{"unique_categories": 5}'},
    
    # =============================================================================
    # SOCIAL/FRIENDS BADGES (6)
    # =============================================================================
    {"code": "first_friend", "name": "Premier Ami", "description": "Ajouter ton premier ami", "icon": "🤝", "rarity": "common", "xp_reward": 20, "condition_type": "friends", "condition_value": '{"min_friends": 1}'},
    {"code": "sociable", "name": "Sociable", "description": "Avoir 5 amis", "icon": "👥", "rarity": "uncommon", "xp_reward": 50, "condition_type": "friends", "condition_value": '{"min_friends": 5}'},
    {"code": "social_butterfly", "name": "Papillon Social", "description": "Avoir 10 amis", "icon": "🦋", "rarity": "rare", "xp_reward": 100, "condition_type": "friends", "condition_value": '{"min_friends": 10}'},
    {"code": "influencer", "name": "Influenceur", "description": "Avoir 25 amis", "icon": "⭐", "rarity": "epic", "xp_reward": 200, "condition_type": "friends", "condition_value": '{"min_friends": 25}'},
    {"code": "community_leader", "name": "Leader Communautaire", "description": "Avoir 50 amis", "icon": "👑", "rarity": "legendary", "xp_reward": 400, "condition_type": "friends", "condition_value": '{"min_friends": 50}'},
    {"code": "helpful", "name": "Âme Charitable", "description": "Encourager 10 amis", "icon": "💝", "rarity": "rare", "xp_reward": 75, "condition_type": "friends", "condition_value": '{"encouragements_sent": 10}'},
    
    # =============================================================================
    # SHOP/PURCHASES BADGES (4)
    # =============================================================================
    {"code": "first_purchase", "name": "Premier Achat", "description": "Acheter ton premier item", "icon": "🛒", "rarity": "common", "xp_reward": 15, "condition_type": "purchases", "condition_value": '{"count": 1}'},
    {"code": "shopaholic", "name": "Accro au Shopping", "description": "Acheter 10 items dans la boutique", "icon": "🛍️", "rarity": "rare", "xp_reward": 100, "condition_type": "purchases", "condition_value": '{"count": 10}'},
    {"code": "collector", "name": "Collectionneur", "description": "Acheter 25 items différents", "icon": "🎁", "rarity": "epic", "xp_reward": 200, "condition_type": "purchases", "condition_value": '{"unique_items": 25}'},
    {"code": "big_spender", "name": "Grand Dépensier", "description": "Dépenser 5000 pièces au total", "icon": "💸", "rarity": "epic", "xp_reward": 200, "condition_type": "purchases", "condition_value": '{"total_spent": 5000}'},
    
    # =============================================================================
    # SEASONAL BADGES (6)
    # =============================================================================
    {"code": "new_year", "name": "Bonne Année!", "description": "Jouer le jour de l'An", "icon": "🎆", "rarity": "seasonal", "xp_reward": 50, "condition_type": "date", "condition_value": '{"date": "01-01"}', "is_seasonal": True},
    {"code": "valentine", "name": "Saint Valentin", "description": "Jouer le 14 février", "icon": "💕", "rarity": "seasonal", "xp_reward": 50, "condition_type": "date", "condition_value": '{"date": "02-14"}', "is_seasonal": True},
    {"code": "summer_vibes", "name": "Vibes d'Été", "description": "Jouer pendant le solstice d'été", "icon": "☀️", "rarity": "seasonal", "xp_reward": 50, "condition_type": "date", "condition_value": '{"start_date": "06-20", "end_date": "06-22"}', "is_seasonal": True},
    {"code": "halloween", "name": "Trick or Treat", "description": "Jouer à Halloween", "icon": "🎃", "rarity": "seasonal", "xp_reward": 50, "condition_type": "date", "condition_value": '{"date": "10-31"}', "is_seasonal": True},
    {"code": "christmas", "name": "Joyeux Noël", "description": "Jouer à Noël", "icon": "🎄", "rarity": "seasonal", "xp_reward": 50, "condition_type": "date", "condition_value": '{"start_date": "12-24", "end_date": "12-26"}', "is_seasonal": True},
    {"code": "birthday", "name": "Bon Anniversaire!", "description": "Jouer le jour de ton anniversaire", "icon": "🎂", "rarity": "seasonal", "xp_reward": 100, "condition_type": "date", "condition_value": '{"type": "birthday"}', "is_seasonal": True},
    
    # =============================================================================
    # SECRET BADGES (4)
    # =============================================================================
    {"code": "comeback_kid", "name": "Le Retour", "description": "???", "icon": "🔙", "rarity": "secret", "xp_reward": 75, "condition_type": "secret", "condition_value": '{"secret_type": "comeback"}', "is_secret": True},
    {"code": "perfectionist", "name": "Perfectionniste", "description": "???", "icon": "✨", "rarity": "secret", "xp_reward": 150, "condition_type": "secret", "condition_value": '{"secret_type": "perfectionist"}', "is_secret": True},
    {"code": "phoenix", "name": "Phénix", "description": "???", "icon": "🔥", "rarity": "secret", "xp_reward": 100, "condition_type": "secret", "condition_value": '{"secret_type": "first_fail"}', "is_secret": True},
    {"code": "explorer", "name": "Explorateur", "description": "???", "icon": "🗺️", "rarity": "secret", "xp_reward": 50, "condition_type": "secret", "condition_value": '{"secret_type": "all_features"}', "is_secret": True},
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
        skipped = 0
        
        print(f"📋 Total badges to seed: {len(BADGES)}")
        print(f"📦 Existing badges in DB: {len(existing_codes)}")
        print("-" * 50)
        
        for badge in BADGES:
            if badge["code"] in existing_codes:
                skipped += 1
                continue
            
            is_secret = badge.get("is_secret", False)
            is_seasonal = badge.get("is_seasonal", False)
            
            await session.execute(
                text("""
                    INSERT INTO badges (id, code, name, description, icon, rarity, xp_reward, condition_type, condition_value, is_secret, is_seasonal)
                    VALUES (:id, :code, :name, :description, :icon, :rarity, :xp_reward, :condition_type, :condition_value::jsonb, :is_secret, :is_seasonal)
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
                    "is_secret": is_secret,
                    "is_seasonal": is_seasonal,
                }
            )
            inserted += 1
            print(f"  ✅ Added: {badge['icon']} {badge['code']} ({badge['rarity']})")
        
        await session.commit()
        
        print("-" * 50)
        print(f"✅ Inserted: {inserted} new badges")
        print(f"⏭️  Skipped: {skipped} existing badges")
        print(f"📊 Total in DB: {len(existing_codes) + inserted}")
    
    await engine.dispose()


async def list_badges():
    """List all badges in database."""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            text("SELECT code, name, rarity, icon FROM badges ORDER BY rarity, code")
        )
        badges = result.fetchall()
        
        print(f"\n📋 Badges in database: {len(badges)}")
        print("-" * 50)
        
        current_rarity = None
        for code, name, rarity, icon in badges:
            if rarity != current_rarity:
                current_rarity = rarity
                print(f"\n[{rarity.upper()}]")
            print(f"  {icon} {code}: {name}")
    
    await engine.dispose()


if __name__ == "__main__":
    import sys
    
    print("🏆 HabitQuest Badge Seeder")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        asyncio.run(list_badges())
    else:
        asyncio.run(seed_badges())
    
    print("\n✅ Done!")
