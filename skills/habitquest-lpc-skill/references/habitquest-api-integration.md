# Intégration API Backend — FastAPI + SQLAlchemy

Patterns pour le backend HabitQuest : modèles, schémas, et routes pour le système de personnage.

---

## Modèle SQLAlchemy — Character

```python
# backend/app/models/character.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(50), nullable=False, default="Aventurier")
    
    # Progression
    level = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    gold = Column(Integer, default=100, nullable=False)  # Monnaie pour la boutique
    
    # Apparence (stockée en JSON pour flexibilité)
    appearance = Column(JSON, default={
        "bodyType": "male",
        "skinColor": "light",
        "hairStyle": "messy",
        "hairColor": "brown",
        "ears": "human",
    })
    
    # Équipement (noms des items équipés)
    equipment = Column(JSON, default={
        "torso": None,
        "legs": "pants_teal",
        "feet": None,
        "weapon": None,
        "shield": None,
        "headGear": None,
        "cape": None,
    })
    
    # Spritesheet composé (URL vers le PNG généré)
    sprite_sheet_url = Column(String, nullable=True)
    
    # Items débloqués (liste d'IDs)
    unlocked_items = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="character")


class ShopItem(Base):
    """Items disponibles dans la boutique, liés aux assets LPC."""
    __tablename__ = "shop_items"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    slot = Column(String(20), nullable=False)           # torso, legs, weapon, etc.
    sprite_layer = Column(String(200), nullable=False)  # Chemin dans le repo LPC
    required_level = Column(Integer, default=1)
    cost = Column(Integer, default=0)                   # Prix en gold
    rarity = Column(String(20), default="common")       # common, uncommon, rare, epic, legendary
```

---

## Schémas Pydantic V2

```python
# backend/app/schemas/character.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# --- Sous-schémas ---

class AppearanceSchema(BaseModel):
    bodyType: str = "male"
    skinColor: str = "light"
    hairStyle: str = "messy"
    hairColor: str = "brown"
    ears: str = "human"


class EquipmentSchema(BaseModel):
    torso: Optional[str] = None
    legs: Optional[str] = None
    feet: Optional[str] = None
    weapon: Optional[str] = None
    shield: Optional[str] = None
    headGear: Optional[str] = None
    cape: Optional[str] = None


# --- Réponses ---

class CharacterResponse(BaseModel):
    id: str
    userId: str = Field(alias="user_id")
    name: str
    level: int
    xp: int
    xpToNextLevel: int = Field(default=100)
    gold: int
    appearance: AppearanceSchema
    equipment: EquipmentSchema
    spriteSheetUrl: Optional[str] = Field(alias="sprite_sheet_url")
    unlockedItems: list[str] = Field(alias="unlocked_items", default=[])
    createdAt: datetime = Field(alias="created_at")
    updatedAt: Optional[datetime] = Field(alias="updated_at")

    class Config:
        from_attributes = True
        populate_by_name = True


# --- Mises à jour ---

class CharacterUpdateRequest(BaseModel):
    name: Optional[str] = None
    appearance: Optional[AppearanceSchema] = None
    equipment: Optional[EquipmentSchema] = None
    spriteSheetUrl: Optional[str] = None


# --- Boutique ---

class ShopItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    slot: str
    spriteLayer: str = Field(alias="sprite_layer")
    requiredLevel: int = Field(alias="required_level")
    cost: int
    rarity: str

    class Config:
        from_attributes = True
        populate_by_name = True


class PurchaseRequest(BaseModel):
    itemId: str


class PurchaseResponse(BaseModel):
    success: bool
    message: str
    remainingGold: int
    character: CharacterResponse
```

---

## Routes FastAPI

```python
# backend/app/routers/characters.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.character import Character, ShopItem
from app.schemas.character import (
    CharacterResponse,
    CharacterUpdateRequest,
    ShopItemResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.dependencies import get_current_user
from app.services.progression import calculate_xp_to_next_level
import uuid

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/me", response_model=CharacterResponse)
async def get_my_character(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupère le personnage de l'utilisateur connecté."""
    character = db.query(Character).filter(
        Character.user_id == current_user.id
    ).first()

    if not character:
        # Auto-création du personnage au premier accès
        character = Character(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=current_user.username or "Aventurier",
        )
        db.add(character)
        db.commit()
        db.refresh(character)

    # Calculer XP pour le prochain niveau
    character.xp_to_next_level = calculate_xp_to_next_level(character.level)
    return character


@router.patch("/me", response_model=CharacterResponse)
async def update_my_character(
    update: CharacterUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Met à jour le personnage (nom, apparence, équipement, spritesheet)."""
    character = db.query(Character).filter(
        Character.user_id == current_user.id
    ).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if update.name is not None:
        character.name = update.name
    if update.appearance is not None:
        character.appearance = update.appearance.model_dump()
    if update.equipment is not None:
        character.equipment = update.equipment.model_dump()
    if update.spriteSheetUrl is not None:
        character.sprite_sheet_url = update.spriteSheetUrl

    db.commit()
    db.refresh(character)
    character.xp_to_next_level = calculate_xp_to_next_level(character.level)
    return character


# --- Boutique ---

shop_router = APIRouter(prefix="/api/shop", tags=["shop"])


@shop_router.get("/items", response_model=list[ShopItemResponse])
async def list_shop_items(
    slot: str | None = None,
    max_level: int | None = None,
    db: Session = Depends(get_db),
):
    """Liste les items disponibles dans la boutique."""
    query = db.query(ShopItem)
    if slot:
        query = query.filter(ShopItem.slot == slot)
    if max_level:
        query = query.filter(ShopItem.required_level <= max_level)
    return query.order_by(ShopItem.required_level, ShopItem.cost).all()


@shop_router.post("/purchase", response_model=PurchaseResponse)
async def purchase_item(
    req: PurchaseRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Achète un item de la boutique."""
    character = db.query(Character).filter(
        Character.user_id == current_user.id
    ).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    item = db.query(ShopItem).filter(ShopItem.id == req.itemId).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Vérifications
    if character.level < item.required_level:
        raise HTTPException(
            status_code=403,
            detail=f"Niveau {item.required_level} requis (vous êtes niveau {character.level})"
        )
    if character.gold < item.cost:
        raise HTTPException(
            status_code=403,
            detail=f"Pas assez d'or ({character.gold}/{item.cost})"
        )
    if item.id in (character.unlocked_items or []):
        raise HTTPException(status_code=409, detail="Item déjà débloqué")

    # Achat
    character.gold -= item.cost
    unlocked = list(character.unlocked_items or [])
    unlocked.append(item.id)
    character.unlocked_items = unlocked

    db.commit()
    db.refresh(character)
    character.xp_to_next_level = calculate_xp_to_next_level(character.level)

    return PurchaseResponse(
        success=True,
        message=f"'{item.name}' acheté avec succès !",
        remainingGold=character.gold,
        character=character,
    )
```

---

## Service de progression

```python
# backend/app/services/progression.py

import math


def calculate_xp_to_next_level(level: int) -> int:
    """Formule de progression RPG : chaque niveau demande plus d'XP.
    
    Niv 1 → 100 XP
    Niv 2 → 150 XP
    Niv 5 → 325 XP
    Niv 10 → 700 XP
    Niv 20 → 2000 XP
    """
    return int(100 * (1 + (level - 1) * 0.5) + 50 * math.floor(level / 5))


def xp_for_habit_completion(habit_difficulty: str, streak: int) -> int:
    """XP gagnée en complétant une habitude.
    
    Bonus de streak : +10% par jour de streak (max +100%)
    """
    base_xp = {
        "easy": 10,
        "medium": 20,
        "hard": 40,
        "epic": 75,
    }.get(habit_difficulty, 15)

    streak_bonus = min(streak * 0.1, 1.0)  # max 100% bonus
    return int(base_xp * (1 + streak_bonus))


def gold_for_habit_completion(habit_difficulty: str) -> int:
    """Or gagné en complétant une habitude."""
    return {
        "easy": 5,
        "medium": 10,
        "hard": 20,
        "epic": 40,
    }.get(habit_difficulty, 8)


def check_level_up(character) -> bool:
    """Vérifie et applique le level up si assez d'XP.
    
    Retourne True si le personnage a gagné un niveau.
    """
    xp_needed = calculate_xp_to_next_level(character.level)
    if character.xp >= xp_needed:
        character.xp -= xp_needed
        character.level += 1
        return True
    return False
```

---

## Migration Alembic

```python
# backend/alembic/versions/xxxx_add_character_tables.py
# (générer avec : alembic revision --autogenerate -m "add character tables")

"""add character tables

Revision ID: xxxx
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    op.create_table(
        'characters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False, server_default='Aventurier'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('gold', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('appearance', JSON(), nullable=True),
        sa.Column('equipment', JSON(), nullable=True),
        sa.Column('sprite_sheet_url', sa.String(), nullable=True),
        sa.Column('unlocked_items', JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_characters_user_id', 'characters', ['user_id'])

    op.create_table(
        'shop_items',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('slot', sa.String(20), nullable=False),
        sa.Column('sprite_layer', sa.String(200), nullable=False),
        sa.Column('required_level', sa.Integer(), server_default='1'),
        sa.Column('cost', sa.Integer(), server_default='0'),
        sa.Column('rarity', sa.String(20), server_default='common'),
    )


def downgrade():
    op.drop_table('shop_items')
    op.drop_table('characters')
```

---

## Seed data — Items de boutique de départ

```python
# backend/scripts/seed_shop_items.py

STARTER_ITEMS = [
    # === Niveau 1 — Départ gratuit ===
    {"id": "legs_pants_teal", "name": "Pantalon basique", "slot": "legs",
     "sprite_layer": "legs/pants/male/teal.png", "required_level": 1, "cost": 0,
     "rarity": "common", "description": "Un pantalon simple pour commencer."},

    # === Niveau 2-5 — Premiers achats ===
    {"id": "feet_boots_brown", "name": "Bottes en cuir", "slot": "feet",
     "sprite_layer": "feet/shoes/male/brown.png", "required_level": 2, "cost": 50,
     "rarity": "common", "description": "Des bottes solides pour l'aventure."},
    {"id": "torso_shirt_white", "name": "Chemise blanche", "slot": "torso",
     "sprite_layer": "torso/shirts/male/white.png", "required_level": 3, "cost": 75,
     "rarity": "common", "description": "Une chemise propre et confortable."},
    {"id": "weapon_dagger", "name": "Dague", "slot": "weapon",
     "sprite_layer": "weapons/right hand/male/dagger.png", "required_level": 4, "cost": 100,
     "rarity": "common", "description": "Une petite lame pour se défendre."},

    # === Niveau 5-10 — Uncommon ===
    {"id": "torso_leather", "name": "Armure de cuir", "slot": "torso",
     "sprite_layer": "torso/leather/male/brown.png", "required_level": 5, "cost": 200,
     "rarity": "uncommon", "description": "Protection légère mais efficace."},
    {"id": "weapon_longsword", "name": "Épée longue", "slot": "weapon",
     "sprite_layer": "weapons/right hand/male/longsword.png", "required_level": 7, "cost": 300,
     "rarity": "uncommon", "description": "L'arme classique de l'aventurier."},
    {"id": "shield_buckler", "name": "Bouclier rond", "slot": "shield",
     "sprite_layer": "shield/male/buckler.png", "required_level": 8, "cost": 250,
     "rarity": "uncommon", "description": "Un petit bouclier pratique."},

    # === Niveau 10-15 — Rare ===
    {"id": "torso_chain", "name": "Cotte de mailles", "slot": "torso",
     "sprite_layer": "torso/chainmail/male/steel.png", "required_level": 10, "cost": 500,
     "rarity": "rare", "description": "Armure de mailles solide."},
    {"id": "headgear_helm_steel", "name": "Casque en acier", "slot": "headGear",
     "sprite_layer": "head/helms/male/steel.png", "required_level": 12, "cost": 450,
     "rarity": "rare", "description": "Protection fiable pour la tête."},
    {"id": "cape_blue", "name": "Cape bleue", "slot": "cape",
     "sprite_layer": "cape/male/blue.png", "required_level": 10, "cost": 350,
     "rarity": "rare", "description": "Une cape qui flotte au vent."},

    # === Niveau 15-20 — Epic ===
    {"id": "torso_plate", "name": "Armure de plaques", "slot": "torso",
     "sprite_layer": "torso/plate/male/gold.png", "required_level": 15, "cost": 1000,
     "rarity": "epic", "description": "Armure lourde dorée — impressionnante."},
    {"id": "weapon_greatsword", "name": "Épée à deux mains", "slot": "weapon",
     "sprite_layer": "weapons/right hand/male/greatsword.png", "required_level": 18, "cost": 1200,
     "rarity": "epic", "description": "Arme massive qui inspire le respect."},

    # === Niveau 20+ — Legendary ===
    {"id": "headgear_crown_gold", "name": "Couronne d'or", "slot": "headGear",
     "sprite_layer": "head/helms/male/golden.png", "required_level": 20, "cost": 2500,
     "rarity": "legendary", "description": "La couronne des plus disciplinés."},
    {"id": "cape_purple", "name": "Cape royale", "slot": "cape",
     "sprite_layer": "cape/male/purple.png", "required_level": 25, "cost": 3000,
     "rarity": "legendary", "description": "Signe de maîtrise ultime."},
]
```

---

## Enregistrement des routes dans main.py

```python
# Dans backend/app/main.py — ajouter :
from app.routers.characters import router as characters_router, shop_router

app.include_router(characters_router)
app.include_router(shop_router)
```
