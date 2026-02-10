"""
Seed script for shop items.

Run with: docker compose exec backend python scripts/seed_items.py
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4
from sqlalchemy import select
from app.database import async_engine, get_db, AsyncSession
from app.models.item import Item


ITEMS = [
    # ============ WEAPONS ============
    # Common
    {
        "name": "Épée en bois",
        "description": "Une épée d'entraînement basique.",
        "category": "weapon",
        "rarity": "common",
        "price": 50,
        "strength_bonus": 2,
        "sprite_url": "/sprites/items/sword_wood.png",
    },
    {
        "name": "Bâton d'apprenti",
        "description": "Un bâton simple pour les apprentis mages.",
        "category": "weapon",
        "rarity": "common",
        "price": 50,
        "intelligence_bonus": 2,
        "sprite_url": "/sprites/items/staff_basic.png",
    },
    {
        "name": "Dague rouillée",
        "description": "Une vieille dague trouvée dans une cave.",
        "category": "weapon",
        "rarity": "common",
        "price": 40,
        "agility_bonus": 2,
        "sprite_url": "/sprites/items/dagger_rusty.png",
    },
    # Uncommon
    {
        "name": "Épée en fer",
        "description": "Une épée solide forgée par un apprenti forgeron.",
        "category": "weapon",
        "rarity": "uncommon",
        "price": 120,
        "strength_bonus": 5,
        "sprite_url": "/sprites/items/sword_iron.png",
    },
    {
        "name": "Bâton runique",
        "description": "Un bâton gravé de runes mystiques.",
        "category": "weapon",
        "rarity": "uncommon",
        "price": 130,
        "intelligence_bonus": 5,
        "strength_bonus": 1,
        "sprite_url": "/sprites/items/staff_rune.png",
    },
    {
        "name": "Arc sylvestre",
        "description": "Un arc fabriqué par les elfes des bois.",
        "category": "weapon",
        "rarity": "uncommon",
        "price": 110,
        "agility_bonus": 4,
        "strength_bonus": 2,
        "sprite_url": "/sprites/items/bow_wood.png",
    },
    # Rare
    {
        "name": "Épée enchantée",
        "description": "Une lame qui brille d'une lueur bleue.",
        "category": "weapon",
        "rarity": "rare",
        "price": 250,
        "strength_bonus": 8,
        "intelligence_bonus": 2,
        "sprite_url": "/sprites/items/sword_enchanted.png",
    },
    {
        "name": "Bâton de foudre",
        "description": "Crépite d'énergie électrique.",
        "category": "weapon",
        "rarity": "rare",
        "price": 280,
        "intelligence_bonus": 10,
        "sprite_url": "/sprites/items/staff_lightning.png",
    },
    {
        "name": "Dagues d'ombre",
        "description": "Des lames qui semblent absorber la lumière.",
        "category": "weapon",
        "rarity": "rare",
        "price": 260,
        "agility_bonus": 10,
        "sprite_url": "/sprites/items/daggers_shadow.png",
    },
    # Epic
    {
        "name": "Lame de feu",
        "description": "Une épée enflammée par la magie ancienne.",
        "category": "weapon",
        "rarity": "epic",
        "price": 450,
        "strength_bonus": 12,
        "agility_bonus": 3,
        "sprite_url": "/sprites/items/sword_fire.png",
    },
    {
        "name": "Bâton du sage",
        "description": "Porté par les plus grands mages de l'histoire.",
        "category": "weapon",
        "rarity": "epic",
        "price": 500,
        "intelligence_bonus": 15,
        "charisma_bonus": 3,
        "sprite_url": "/sprites/items/staff_sage.png",
    },
    # Legendary
    {
        "name": "Excalibur",
        "description": "L'épée légendaire des rois.",
        "category": "weapon",
        "rarity": "legendary",
        "price": 1000,
        "strength_bonus": 18,
        "endurance_bonus": 5,
        "charisma_bonus": 5,
        "sprite_url": "/sprites/items/excalibur.png",
    },

    # ============ ARMOR ============
    # Common
    {
        "name": "Tunique simple",
        "description": "Vêtements de base pour voyageur.",
        "category": "armor",
        "rarity": "common",
        "price": 40,
        "endurance_bonus": 2,
        "sprite_url": "/sprites/items/tunic_basic.png",
    },
    {
        "name": "Robe d'apprenti",
        "description": "La robe traditionnelle des novices.",
        "category": "armor",
        "rarity": "common",
        "price": 45,
        "intelligence_bonus": 1,
        "endurance_bonus": 1,
        "sprite_url": "/sprites/items/robe_basic.png",
    },
    # Uncommon
    {
        "name": "Armure de cuir",
        "description": "Protection légère mais efficace.",
        "category": "armor",
        "rarity": "uncommon",
        "price": 100,
        "endurance_bonus": 5,
        "sprite_url": "/sprites/items/armor_leather.png",
    },
    {
        "name": "Robe enchantée",
        "description": "Tissée avec des fils magiques.",
        "category": "armor",
        "rarity": "uncommon",
        "price": 120,
        "endurance_bonus": 3,
        "intelligence_bonus": 4,
        "sprite_url": "/sprites/items/robe_enchanted.png",
    },
    # Rare
    {
        "name": "Cotte de mailles",
        "description": "Armure classique des chevaliers.",
        "category": "armor",
        "rarity": "rare",
        "price": 220,
        "endurance_bonus": 8,
        "strength_bonus": 2,
        "sprite_url": "/sprites/items/chainmail.png",
    },
    {
        "name": "Armure de l'ombre",
        "description": "Armure légère qui fond dans les ténèbres.",
        "category": "armor",
        "rarity": "rare",
        "price": 240,
        "endurance_bonus": 5,
        "agility_bonus": 6,
        "sprite_url": "/sprites/items/armor_shadow.png",
    },
    # Epic
    {
        "name": "Armure de plates",
        "description": "Protection maximale pour les guerriers.",
        "category": "armor",
        "rarity": "epic",
        "price": 400,
        "endurance_bonus": 12,
        "strength_bonus": 4,
        "sprite_url": "/sprites/items/armor_plate.png",
    },
    {
        "name": "Robe de l'archimage",
        "description": "Portée par les maîtres de la magie.",
        "category": "armor",
        "rarity": "epic",
        "price": 420,
        "endurance_bonus": 6,
        "intelligence_bonus": 12,
        "sprite_url": "/sprites/items/robe_archmage.png",
    },
    # Legendary
    {
        "name": "Armure draconique",
        "description": "Forgée dans les écailles d'un dragon ancien.",
        "category": "armor",
        "rarity": "legendary",
        "price": 900,
        "endurance_bonus": 18,
        "strength_bonus": 6,
        "agility_bonus": -2,
        "sprite_url": "/sprites/items/armor_dragon.png",
    },

    # ============ HELMET ============
    # Common
    {
        "name": "Capuche",
        "description": "Une simple capuche de voyage.",
        "category": "helmet",
        "rarity": "common",
        "price": 30,
        "agility_bonus": 1,
        "sprite_url": "/sprites/items/hood_basic.png",
    },
    # Uncommon
    {
        "name": "Casque de cuir",
        "description": "Protection basique pour la tête.",
        "category": "helmet",
        "rarity": "uncommon",
        "price": 70,
        "endurance_bonus": 3,
        "sprite_url": "/sprites/items/helmet_leather.png",
    },
    # Rare
    {
        "name": "Heaume de fer",
        "description": "Casque complet de chevalier.",
        "category": "helmet",
        "rarity": "rare",
        "price": 180,
        "endurance_bonus": 5,
        "strength_bonus": 2,
        "sprite_url": "/sprites/items/helmet_iron.png",
    },
    {
        "name": "Diadème magique",
        "description": "Amplifie les capacités mentales.",
        "category": "helmet",
        "rarity": "rare",
        "price": 200,
        "intelligence_bonus": 6,
        "charisma_bonus": 2,
        "sprite_url": "/sprites/items/tiara_magic.png",
    },
    # Epic
    {
        "name": "Heaume du champion",
        "description": "Porté par les plus grands guerriers.",
        "category": "helmet",
        "rarity": "epic",
        "price": 350,
        "endurance_bonus": 8,
        "strength_bonus": 4,
        "sprite_url": "/sprites/items/helmet_champion.png",
    },
    # Legendary
    {
        "name": "Couronne royale",
        "description": "La couronne des anciens rois.",
        "category": "helmet",
        "rarity": "legendary",
        "price": 800,
        "charisma_bonus": 10,
        "intelligence_bonus": 5,
        "endurance_bonus": 3,
        "sprite_url": "/sprites/items/crown_royal.png",
    },

    # ============ ACCESSORY ============
    # Common
    {
        "name": "Cape simple",
        "description": "Une cape de voyage ordinaire.",
        "category": "accessory",
        "rarity": "common",
        "price": 35,
        "charisma_bonus": 1,
        "sprite_url": "/sprites/items/cape_basic.png",
    },
    {
        "name": "Anneau de cuivre",
        "description": "Un simple anneau décoratif.",
        "category": "accessory",
        "rarity": "common",
        "price": 25,
        "endurance_bonus": 1,
        "sprite_url": "/sprites/items/ring_copper.png",
    },
    # Uncommon
    {
        "name": "Cape brodée",
        "description": "Une belle cape avec des broderies.",
        "category": "accessory",
        "rarity": "uncommon",
        "price": 90,
        "charisma_bonus": 3,
        "sprite_url": "/sprites/items/cape_embroidered.png",
    },
    {
        "name": "Amulette de protection",
        "description": "Offre une légère protection magique.",
        "category": "accessory",
        "rarity": "uncommon",
        "price": 100,
        "endurance_bonus": 3,
        "intelligence_bonus": 1,
        "sprite_url": "/sprites/items/amulet_protection.png",
    },
    # Rare
    {
        "name": "Cape royale",
        "description": "Bordée de fourrure noble.",
        "category": "accessory",
        "rarity": "rare",
        "price": 200,
        "charisma_bonus": 6,
        "endurance_bonus": 2,
        "sprite_url": "/sprites/items/cape_royal.png",
    },
    {
        "name": "Anneau de force",
        "description": "Augmente la puissance physique.",
        "category": "accessory",
        "rarity": "rare",
        "price": 180,
        "strength_bonus": 5,
        "sprite_url": "/sprites/items/ring_strength.png",
    },
    {
        "name": "Amulette de sagesse",
        "description": "Clarifie l'esprit de son porteur.",
        "category": "accessory",
        "rarity": "rare",
        "price": 190,
        "intelligence_bonus": 5,
        "sprite_url": "/sprites/items/amulet_wisdom.png",
    },
    # Epic
    {
        "name": "Cape du vent",
        "description": "Permet de se déplacer comme le vent.",
        "category": "accessory",
        "rarity": "epic",
        "price": 380,
        "agility_bonus": 10,
        "charisma_bonus": 3,
        "sprite_url": "/sprites/items/cape_wind.png",
    },
    {
        "name": "Anneau du dragon",
        "description": "Contient l'essence d'un dragon.",
        "category": "accessory",
        "rarity": "epic",
        "price": 400,
        "strength_bonus": 6,
        "endurance_bonus": 6,
        "sprite_url": "/sprites/items/ring_dragon.png",
    },
    # Legendary
    {
        "name": "Cape légendaire",
        "description": "Flotte majestueusement, effet de particules.",
        "category": "accessory",
        "rarity": "legendary",
        "price": 750,
        "charisma_bonus": 10,
        "agility_bonus": 5,
        "endurance_bonus": 3,
        "sprite_url": "/sprites/items/cape_legendary.png",
    },
    {
        "name": "Collier de l'immortel",
        "description": "Porté par ceux qui ont vaincu la mort.",
        "category": "accessory",
        "rarity": "legendary",
        "price": 850,
        "endurance_bonus": 12,
        "intelligence_bonus": 6,
        "sprite_url": "/sprites/items/necklace_immortal.png",
    },
]


async def seed_items():
    """Seed the database with items."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        # Check if items already exist
        result = await db.execute(select(Item).limit(1))
        if result.scalar_one_or_none():
            print("Items already seeded, skipping...")
            return
        
        print(f"Seeding {len(ITEMS)} items...")
        
        for item_data in ITEMS:
            item = Item(
                id=uuid4(),
                name=item_data["name"],
                description=item_data.get("description"),
                category=item_data["category"],
                rarity=item_data["rarity"],
                price=item_data["price"],
                strength_bonus=item_data.get("strength_bonus", 0),
                endurance_bonus=item_data.get("endurance_bonus", 0),
                agility_bonus=item_data.get("agility_bonus", 0),
                intelligence_bonus=item_data.get("intelligence_bonus", 0),
                charisma_bonus=item_data.get("charisma_bonus", 0),
                sprite_url=item_data.get("sprite_url"),
                is_available=True,
                is_limited=False,
                required_level=1,
            )
            db.add(item)
        
        await db.commit()
        print(f"✅ Successfully seeded {len(ITEMS)} items!")


if __name__ == "__main__":
    asyncio.run(seed_items())
