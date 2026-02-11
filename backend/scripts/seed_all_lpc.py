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

# TOUS les items LPC basés sur les sprites disponibles
ALL_LPC_ITEMS = [
    # ==================== ARMES - ÉPÉES ====================
    {'name': 'Dague', 'description': 'Petite lame rapide et discrète.', 'category': 'weapon', 'rarity': 'common', 'price': 30, 'agility_bonus': 3, 'sprite_url': '/sprites/shop/weapons/swords/dagger.png'},
    {'name': 'Épée longue', 'description': 'Épée classique du chevalier.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 120, 'strength_bonus': 5, 'sprite_url': '/sprites/shop/weapons/swords/longsword.png'},
    {'name': 'Rapière', 'description': 'Lame fine et élégante pour les duellistes.', 'category': 'weapon', 'rarity': 'rare', 'price': 200, 'agility_bonus': 6, 'strength_bonus': 2, 'sprite_url': '/sprites/shop/weapons/swords/rapier.png'},
    {'name': 'Sabre', 'description': 'Lame courbée des pirates et cavaliers.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 100, 'strength_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/weapons/swords/saber.png'},
    
    # ==================== ARMES - CONTONDANTES ====================
    {'name': 'Masse', 'description': 'Arme lourde et dévastatrice.', 'category': 'weapon', 'rarity': 'uncommon', 'price': 110, 'strength_bonus': 6, 'sprite_url': '/sprites/shop/weapons/blunt/mace.png'},
    {'name': 'Fléau', 'description': 'Chaîne et boule de métal. Dévastateur.', 'category': 'weapon', 'rarity': 'rare', 'price': 220, 'strength_bonus': 8, 'sprite_url': '/sprites/shop/weapons/blunt/flail.png'},
    
    # ==================== ARMES - POLEARMS ====================
    {'name': 'Hallebarde', 'description': 'Arme des gardes royaux.', 'category': 'weapon', 'rarity': 'epic', 'price': 350, 'strength_bonus': 10, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/weapons/polearm/halberd.png'},
    
    # ==================== ARMURES - CUIR ====================
    {'name': 'Armure cuir brun (H)', 'description': 'Protection légère en cuir tanné.', 'category': 'armor', 'rarity': 'uncommon', 'price': 100, 'endurance_bonus': 4, 'sprite_url': '/sprites/shop/armor/leather/brown_male.png'},
    {'name': 'Armure cuir brun (F)', 'description': 'Protection légère en cuir tanné.', 'category': 'armor', 'rarity': 'uncommon', 'price': 100, 'endurance_bonus': 4, 'sprite_url': '/sprites/shop/armor/leather/brown_female.png'},
    {'name': 'Armure cuir noir (H)', 'description': 'Cuir sombre pour les rôdeurs.', 'category': 'armor', 'rarity': 'uncommon', 'price': 120, 'endurance_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/armor/leather/black_male.png'},
    {'name': 'Armure cuir noir (F)', 'description': 'Cuir sombre pour les rôdeurs.', 'category': 'armor', 'rarity': 'uncommon', 'price': 120, 'endurance_bonus': 4, 'agility_bonus': 2, 'sprite_url': '/sprites/shop/armor/leather/black_female.png'},
    
    # ==================== ARMURES - PLATES ====================
    {'name': 'Armure plates dorée (H)', 'description': 'Armure resplendissante des champions.', 'category': 'armor', 'rarity': 'epic', 'price': 400, 'endurance_bonus': 12, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/armor/plate/gold_male.png'},
    {'name': 'Armure plates dorée (F)', 'description': 'Armure resplendissante des champions.', 'category': 'armor', 'rarity': 'epic', 'price': 400, 'endurance_bonus': 12, 'charisma_bonus': 3, 'sprite_url': '/sprites/shop/armor/plate/gold_female.png'},
    {'name': 'Armure plates argentée (H)', 'description': 'Armure noble des chevaliers.', 'category': 'armor', 'rarity': 'epic', 'price': 380, 'endurance_bonus': 11, 'strength_bonus': 2, 'sprite_url': '/sprites/shop/armor/plate/silver_male.png'},
    {'name': 'Armure plates argentée (F)', 'description': 'Armure noble des chevaliers.', 'category': 'armor', 'rarity': 'epic', 'price': 380, 'endurance_bonus': 11, 'strength_bonus': 2, 'sprite_url': '/sprites/shop/armor/plate/silver_female.png'},
    {'name': 'Armure plates bronze (H)', 'description': 'Armure solide en bronze.', 'category': 'armor', 'rarity': 'rare', 'price': 280, 'endurance_bonus': 9, 'strength_bonus': 1, 'sprite_url': '/sprites/shop/armor/plate/bronze_male.png'},
    
    # ==================== CHAUSSURES ====================
    {'name': 'Chaussures brunes', 'description': 'Chaussures robustes en cuir.', 'category': 'accessory', 'rarity': 'common', 'price': 35, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/feet/shoes_brown.png'},
    {'name': 'Chaussures noires', 'description': 'Chaussures élégantes.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/feet/shoes_black.png'},
    
    # ==================== PANTALONS ====================
    {'name': 'Pantalon turquoise', 'description': 'Pantalon confortable et coloré.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_teal.png'},
    {'name': 'Pantalon rouge', 'description': 'Pantalon audacieux.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_red.png'},
    {'name': 'Pantalon noir', 'description': 'Pantalon classique et sobre.', 'category': 'accessory', 'rarity': 'common', 'price': 35, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_black.png'},
    {'name': 'Pantalon blanc', 'description': 'Pantalon immaculé.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 50, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/legs/pants_white.png'},
    {'name': 'Pantalon vert', 'description': 'Pantalon forestier.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'agility_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_green.png'},
    {'name': 'Pantalon bleu', 'description': 'Pantalon élégant.', 'category': 'accessory', 'rarity': 'common', 'price': 40, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/legs/pants_blue.png'},
    
    # ==================== COIFFURES MASCULINES ====================
    {'name': 'Cheveux courts noirs (H)', 'description': 'Coupe courte pratique.', 'category': 'accessory', 'rarity': 'common', 'price': 50, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/hair/bangsshort_black_m.png'},
    {'name': 'Cheveux courts blonds (H)', 'description': 'Coupe courte blonde.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 70, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/bangsshort_blonde_m.png'},
    {'name': 'Cheveux longs noirs (H)', 'description': 'Cheveux longs mystérieux.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 80, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/bangslong_black_m.png'},
    
    # ==================== COIFFURES FÉMININES ====================
    {'name': 'Queue de cheval noire (F)', 'description': 'Coiffure pratique et élégante.', 'category': 'accessory', 'rarity': 'common', 'price': 50, 'charisma_bonus': 1, 'sprite_url': '/sprites/shop/hair/ponytail_black_f.png'},
    {'name': 'Queue de cheval blonde (F)', 'description': 'Coiffure lumineuse.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 70, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/ponytail_blonde_f.png'},
    {'name': 'Queue de cheval rousse (F)', 'description': 'Coiffure flamboyante.', 'category': 'accessory', 'rarity': 'rare', 'price': 120, 'charisma_bonus': 4, 'sprite_url': '/sprites/shop/hair/ponytail_red_f.png'},
    {'name': 'Cheveux lâchés noirs (F)', 'description': 'Cheveux longs et libres.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 80, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/loose_black_f.png'},
    {'name': 'Cheveux longs noirs (F)', 'description': 'Coiffure élégante.', 'category': 'accessory', 'rarity': 'uncommon', 'price': 75, 'charisma_bonus': 2, 'sprite_url': '/sprites/shop/hair/bangslong_black_f.png'},
    
    # ==================== SKINS (BODIES) ====================
    {'name': 'Peau claire (H)', 'description': 'Apparence masculine peau claire.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/male_light.png'},
    {'name': 'Peau foncée (H)', 'description': 'Apparence masculine peau foncée.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/male_dark.png'},
    {'name': 'Peau bronzée (H)', 'description': 'Apparence masculine bronzée.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/male_tanned.png'},
    {'name': 'Peau claire (F)', 'description': 'Apparence féminine peau claire.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/female_light.png'},
    {'name': 'Peau foncée (F)', 'description': 'Apparence féminine peau foncée.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/female_dark.png'},
    {'name': 'Peau bronzée (F)', 'description': 'Apparence féminine bronzée.', 'category': 'accessory', 'rarity': 'common', 'price': 0, 'sprite_url': '/sprites/shop/bodies/female_tanned.png'},
]

async def main():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await db.execute(text('DELETE FROM user_inventory'))
        await db.execute(delete(Item))
        print('🗑️  Base nettoyée')
        
        for item_data in ALL_LPC_ITEMS:
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
        print(f'✅ {len(ALL_LPC_ITEMS)} items LPC ajoutés!')

if __name__ == '__main__':
    asyncio.run(main())
