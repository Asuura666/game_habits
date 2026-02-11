import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4
from sqlalchemy import select
from app.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.item import Item

LPC_ITEMS = [
    {'name': 'Épée longue', 'description': 'Une épée classique de chevalier.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 150, 'strength_bonus': 6, 'sprite_url': '/sprites/shop/weapons/longsword.png'},
    {'name': 'Rapière élégante', 'description': 'Une lame fine pour les duellistes.', 'category': 'weapon', 'rarity': 'rare', 'price': 220, 'agility_bonus': 7, 'strength_bonus': 3, 'sprite_url': '/sprites/shop/weapons/rapier.png'},
    {'name': 'Sabre de pirate', 'description': 'Courbe et tranchant.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 140, 'strength_bonus': 5, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/weapons/saber.png'},
    {'name': 'Dague de l\'assassin', 'description': 'Silencieuse et mortelle.', 'category': 'weapon', 'rarity': 'rare', 'price': 200, 'agility_bonus': 8, 'sprite_url': '/sprites/shop/weapons/dagger.png'},
    {'name': 'Masse d\'armes', 'description': 'Lourde et dévastatrice.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 130, 'strength_bonus': 7, 'sprite_url': '/sprites/shop/weapons/mace.png'},
    {'name': 'Fléau d\'armes', 'description': 'Une chaîne, une boule, beaucoup de dégâts.', 'category': 'weapon', 'rarity': 'rare', 'price': 240, 'strength_bonus': 9, 'sprite_url': '/sprites/shop/weapons/flail.png'},
    {'name': 'Hallebarde', 'description': 'L\'arme des gardes royaux.', 'category': 'weapon', 'rarity': 'epic', 'price': 380, 'strength_bonus': 10, 'agility_bonus': 3, 'sprite_url': '/sprites/shop/weapons/halberd.png'},
    {'name': 'Armure de cuir noir', 'description': 'Cuir tanné pour les rôdeurs.', 'category': 'armor', 'rarity': 'uncommon', 'price': 120, 'endurance_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/armor/leather_black.png'},
    {'name': 'Armure de cuir brun', 'description': 'Protection classique.', 'category': 'armor', 'rarity': 'uncommon', 'price': 110, 'endurance_bonus': 5, 'sprite_url': '/sprites/shop/armor/leather_brown.png'},
    {'name': 'Armure de plates dorée', 'description': 'Resplendissante et protectrice.', 'category': 'armor', 'rarity': 'epic', 'price': 450, 'endurance_bonus': 14, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/armor/plate_gold.png'},
    {'name': 'Armure de plates argentée', 'description': 'La marque des chevaliers nobles.', 'category': 'armor', 'rarity': 'epic', 'price': 420, 'endurance_bonus': 13, 'strength_bonus': 2, 'sprite_url': '/sprites/shop/armor/plate_silver.png'},
    {'name': 'Pantalon turquoise', 'description': 'Élégant et confortable.', 'category': 'accessory', 'rarity': 'common', 'price': 50, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_teal.png'},
    {'name': 'Pantalon rouge', 'description': 'Pour ceux qui n\'ont pas peur.', 'category': 'accessory', 'rarity': 'common', 'price': 50, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_red.png'},
    {'name': 'Chaussures en cuir', 'description': 'Robustes pour la route.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/feet/shoes_brown.png'},
    {'name': 'Coupe courte noire', 'description': 'Style pratique et élégant.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 80, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/bangsshort_black.png'},
    {'name': 'Queue de cheval rousse', 'description': 'Flamboyante et dynamique.', 'category': 'accessory', 'rarity': 'rare', 'price': 150, 'charisma_bonus': 4, 'sprite_url': '/sprites/shop/hair/ponytail_red.png'},
]

async def main():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        # Check which items already exist
        result = await db.execute(select(Item.name))
        existing = {r[0] for r in result.fetchall()}
        
        added = 0
        for item_data in LPC_ITEMS:
            if item_data['name'] not in existing:
                item = Item(
                    id=uuid4(),
                    name=item_data['name'],
                    description=item_data.get('description'),
                    category=item_data['category'],
                    rarity=item_data['rarity'],
                    price=item_data['price'],
                    strength_bonus=item_data.get('strength_bonus', 0),
                    endurance_bonus=item_data.get('endurance_bonus', 0),
                    agility_bonus=item_data.get('agility_bonus', 0),
                    intelligence_bonus=item_data.get('intelligence_bonus', 0),
                    charisma_bonus=item_data.get('charisma_bonus', 0),
                    sprite_url=item_data.get('sprite_url'),
                    is_available=True,
                    is_limited=False,
                    required_level=1,
                )
                db.add(item)
                added += 1
        
        await db.commit()
        print(f'✅ Added {added} new LPC items (total: {len(LPC_ITEMS)})')

if __name__ == '__main__':
    asyncio.run(main())
