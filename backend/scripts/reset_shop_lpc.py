import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import uuid4
from sqlalchemy import delete, text
from app.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.item import Item

LPC_ITEMS = [
    # ARMES
    {'name': 'Dague rouillée', 'description': 'Une vieille dague trouvée.', 'category': 'weapon', 'rarity': 'common', 'price': 30, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/weapons/dagger.png'},
    {'name': 'Épée longue', 'description': 'Épée classique de chevalier.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 120, 'strength_bonus': 5, 'sprite_url': '/sprites/shop/weapons/longsword.png'},
    {'name': 'Sabre de pirate', 'description': 'Courbe et tranchant.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 100, 'strength_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/weapons/saber.png'},
    {'name': 'Masse d\'armes', 'description': 'Lourde et dévastatrice.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 110, 'strength_bonus': 6, 'sprite_url': '/sprites/shop/weapons/mace.png'},
    {'name': 'Rapière élégante', 'description': 'Lame fine pour duellistes.', 'category': 'weapon', 'rarity': 'rare', 'price': 200, 'agility_bonus': 6, 'strength_bonus': 3, 'sprite_url': '/sprites/shop/weapons/rapier.png'},
    {'name': 'Fléau d\'armes', 'description': 'Chaîne et boule de métal.', 'category': 'weapon', 'rarity': 'rare', 'price': 220, 'strength_bonus': 8, 'sprite_url': '/sprites/shop/weapons/flail.png'},
    {'name': 'Hallebarde royale', 'description': 'Arme des gardes royaux.', 'category': 'weapon', 'rarity': 'epic', 'price': 350, 'strength_bonus': 10, 'agility_bonus': 3, 'sprite_url': '/sprites/shop/weapons/halberd.png'},
    # ARMURES
    {'name': 'Chemise blanche', 'description': 'Vêtement de base.', 'category': 'armor', 'rarity': 'common', 'price': 25, 'endurance_bonus': 1, 'sprite_url': '/sprites/shop/armor/shirt_white.png'},
    {'name': 'Chemise bordeaux', 'description': 'Vêtement élégant.', 'category': 'armor', 'rarity': 'common', 'price': 30, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/armor/shirt_maroon.png'},
    {'name': 'Armure de cuir brun', 'description': 'Protection classique.', 'category': 'armor', 'rarity': 'uncommon', 'price': 100, 'endurance_bonus': 4, 'sprite_url': '/sprites/shop/armor/leather_brown.png'},
    {'name': 'Armure de cuir noir', 'description': 'Pour les rôdeurs.', 'category': 'armor', 'rarity': 'uncommon', 'price': 120, 'endurance_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/armor/leather_black.png'},
    {'name': 'Cotte de mailles dorée', 'description': 'Mailles en or.', 'category': 'armor', 'rarity': 'rare', 'price': 250, 'endurance_bonus': 7, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/armor/chainmail_gold.png'},
    {'name': 'Armure de plates dorée', 'description': 'Resplendissante.', 'category': 'armor', 'rarity': 'epic', 'price': 400, 'endurance_bonus': 12, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/armor/plate_gold.png'},
    {'name': 'Armure de plates argentée', 'description': 'Chevalier noble.', 'category': 'armor', 'rarity': 'epic', 'price': 380, 'endurance_bonus': 11, 'strength_bonus': 3, 'sprite_url': '/sprites/shop/armor/plate_silver.png'},
    # CASQUES
    {'name': 'Capuche de mailles', 'description': 'Protection discrète.', 'category': 'helmet', 'rarity': 'rare', 'price': 180, 'endurance_bonus': 5, 'sprite_url': '/sprites/shop/head/chain_hood.png'},
    {'name': 'Heaume doré', 'description': 'Casque de champion.', 'category': 'helmet', 'rarity': 'epic', 'price': 300, 'endurance_bonus': 8, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/head/helm_gold.png'},
    {'name': 'Diadème royal', 'description': 'Couronne des rois.', 'category': 'helmet', 'rarity': 'legendary', 'price': 600, 'charisma_bonus': 10, 'intelligence_bonus': 5, 'sprite_url': '/sprites/shop/head/tiara.png'},
    # BOUCLIERS
    {'name': 'Bouclier rond', 'description': 'Protection basique.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 80, 'endurance_bonus': 3, 'sprite_url': '/sprites/shop/shields/round.png'},
    {'name': 'Targe', 'description': 'Petit bouclier agile.', 'category': 'accessory', 'rarity': 'rare', 'price': 150, 'endurance_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/shields/buckler.png'},
    # CAPES
    {'name': 'Cape bleue', 'description': 'Cape élégante.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 90, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/cape/cape_blue.png'},
    {'name': 'Cape rouge', 'description': 'Cape royale.', 'category': 'accessory', 'rarity': 'rare', 'price': 150, 'charisma_bonus': 5, 'sprite_url': '/sprites/shop/cape/cape_red.png'},
    # PANTALONS
    {'name': 'Pantalon turquoise', 'description': 'Confortable.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_teal.png'},
    {'name': 'Pantalon rouge', 'description': 'Audacieux.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_red.png'},
    # CHAUSSURES
    {'name': 'Chaussures en cuir', 'description': 'Robustes.', 'category': 'accessory', 'rarity': 'common', 'price': 35, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/feet/shoes_brown.png'},
    {'name': 'Bottes dorées', 'description': 'Bottes de parade.', 'category': 'accessory', 'rarity': 'epic', 'price': 280, 'agility_bonus': 5, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/feet/boots_gold.png'},
    # COIFFURES
    {'name': 'Coupe courte noire', 'description': 'Style pratique.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 60, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/bangsshort_black.png'},
    {'name': 'Mohawk blanc', 'description': 'Style punk.', 'category': 'accessory', 'rarity': 'rare', 'price': 120, 'charisma_bonus': 4, 'sprite_url': '/sprites/shop/hair/mohawk_white.png'},
    {'name': 'Queue de cheval rousse', 'description': 'Flamboyante.', 'category': 'accessory', 'rarity': 'rare', 'price': 130, 'charisma_bonus': 4, 'sprite_url': '/sprites/shop/hair/ponytail_red.png'},
]

async def main():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        # Supprimer d'abord les inventaires (foreign key)
        await db.execute(text('DELETE FROM user_inventory'))
        print('🗑️  Inventaires vidés')
        
        # Supprimer tous les items
        await db.execute(delete(Item))
        print('🗑️  Items supprimés')
        
        # Ajouter les items LPC
        for item_data in LPC_ITEMS:
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
        
        await db.commit()
        print(f'✅ {len(LPC_ITEMS)} items LPC ajoutés!')

if __name__ == '__main__':
    asyncio.run(main())
