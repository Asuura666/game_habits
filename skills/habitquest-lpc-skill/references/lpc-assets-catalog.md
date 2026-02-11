# Catalogue des Assets LPC

Ce fichier liste les principales catégories d'assets disponibles dans le générateur LPC.
Source : https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator

## Table des matières
1. [Bodies (Corps)](#bodies)
2. [Heads (Têtes)](#heads)
3. [Hair (Cheveux)](#hair)
4. [Ears (Oreilles)](#ears)
5. [Facial (Pilosité faciale)](#facial)
6. [Torso (Torse / Armures)](#torso)
7. [Legs (Jambes / Pantalons)](#legs)
8. [Feet (Pieds / Chaussures)](#feet)
9. [Weapons (Armes)](#weapons)
10. [Shields (Boucliers)](#shields)
11. [Head Gear (Coiffes)](#head-gear)
12. [Capes](#capes)
13. [Accessories](#accessories)

---

## Bodies

Chaque body est un spritesheet complet couvrant toutes les animations.

### Types de corps disponibles
| Nom | Description | Fichier |
|-----|-------------|---------|
| `male` | Adulte masculin | `body/male/*.png` |
| `female` | Adulte féminin | `body/female/*.png` |
| `muscular` | Musculaire (unisex) | `body/muscular/*.png` |
| `pregnant` | Enceinte | `body/pregnant/*.png` |
| `teen` | Adolescent/androgyne | `body/teen/*.png` |
| `child` | Enfant | `body/child/*.png` |
| `elderly` | Âgé | `body/elderly/*.png` |

### Couleurs de peau (palette LPC standard)
- `light` — peau claire
- `dark` — peau foncée  
- `dark2` — peau très foncée
- `tanned` — bronzé
- `olive` — olive
- `brown` — brun
- `black` — noir
- Fantaisie : `orc`, `red_orc`, `zombie`, `skeleton`

---

## Heads

Les têtes sont séparées des corps depuis LPC Revised (LPCR).
Types : `human`, `reptile`, `wolfman`, `skeleton`

---

## Hair

### Styles de cheveux courants
| Style | Description |
|-------|-------------|
| `bangs` | Frange simple |
| `bangslong` | Frange longue |
| `bangslong2` | Frange longue v2 |
| `bangsshort` | Frange courte |
| `bedhead` | Cheveux ébouriffés |
| `bob` | Carré |
| `braid` | Tresse |
| `bunches` | Couettes |
| `buzzcut` | Coupe rase |
| `cornrows` | Cornrows |
| `curly` | Bouclés |
| `dreadlocks` | Dreadlocks |
| `jewfro` | Afro |
| `long` | Longs |
| `longhawk` | Long hawk |
| `loose` | Lâchés |
| `messy1` | Décoiffé v1 |
| `messy2` | Décoiffé v2 |
| `mohawk` | Mohawk |
| `page` | Coupe au bol |
| `parted` | Raie au milieu |
| `pixie` | Pixie cut |
| `plain` | Simple |
| `ponytail` | Queue de cheval |
| `ponytail2` | Queue de cheval v2 |
| `princess` | Princesse |
| `shorthawk` | Short hawk |
| `shortknot` | Chignon court |
| `shoulderl` | Sur l'épaule gauche |
| `shoulderr` | Sur l'épaule droite |
| `swoop` | Mèche balayée |
| `unkempt` | Négligé |
| `xlong` | Très longs |

### Couleurs de cheveux
- `black`, `blonde`, `blue`, `blue2`, `brown`, `brown2`, `brunette`, `dark_blonde`
- `gold`, `gray`, `green`, `green2`, `light_blonde`, `orange`, `pink`, `pink2`
- `purple`, `raven`, `red`, `red2`, `redhead`, `ruby_red`, `silver`, `white`

---

## Ears

| Type | Description |
|------|-------------|
| `none` | Oreilles humaines par défaut (intégrées au body) |
| `elven` | Oreilles elfiques pointues |
| `elven_long` | Oreilles elfiques longues |

---

## Facial

| Type | Description |
|------|-------------|
| `beard_short` | Barbe courte |
| `beard_long` | Barbe longue |
| `mustache` | Moustache |
| `goatee` | Bouc |
| `stubble` | Barbe de 3 jours |
| `sideburns` | Pattes |

---

## Torso

### Armures et vêtements
| Type | Description |
|------|-------------|
| `leather_armor` | Armure de cuir |
| `chain_armor` | Cotte de mailles |
| `plate_armor` | Armure de plaques |
| `robe` | Robe de mage |
| `shirt_white` | Chemise blanche |
| `shirt_brown` | Chemise brune |
| `tunic` | Tunique |
| `vest` | Gilet |
| `longsleeve` | Manches longues |
| `dress` | Robe (vêtement) |
| `corset` | Corset |

---

## Legs

| Type | Description |
|------|-------------|
| `pants` | Pantalon standard |
| `pants_tight` | Pantalon moulant |
| `shorts` | Short |
| `skirt` | Jupe |
| `robe_skirt` | Bas de robe |
| `loincloth` | Pagne |
| `legion_skirt` | Jupe de légionnaire |

### Couleurs
- `white`, `teal`, `red`, `black`, `brown`, `green`, `blue`, `gray`

---

## Feet

| Type | Description |
|------|-------------|
| `shoes` | Chaussures simples |
| `boots` | Bottes |
| `armor_boots` | Bottes d'armure |
| `sandals` | Sandales |
| `none` | Pieds nus |

### Couleurs
- `brown`, `black`, `gray`, `maroon`

---

## Weapons

### Armes de mêlée
| Type | Description | Animation principale |
|------|-------------|---------------------|
| `longsword` | Épée longue | slash |
| `shortsword` | Épée courte | slash |
| `rapier` | Rapière | thrust |
| `saber` | Sabre | slash |
| `dagger` | Dague | thrust |
| `mace` | Masse | slash |
| `axe` | Hache | slash |
| `waraxe` | Hache de guerre | slash |
| `halberd` | Hallebarde | thrust |
| `spear` | Lance | thrust |
| `flail` | Fléau | slash |
| `warhammer` | Marteau de guerre | slash |

### Armes à distance
| Type | Description | Animation principale |
|------|-------------|---------------------|
| `bow` | Arc | shoot/bow |
| `recurvebow` | Arc recourbé | shoot/bow |
| `crossbow` | Arbalète | shoot |
| `slingshot` | Fronde | shoot |

### Armes magiques
| Type | Description | Animation principale |
|------|-------------|---------------------|
| `staff` | Bâton | spellcast |
| `rod` | Sceptre | spellcast |
| `wand` | Baguette | spellcast |

---

## Shields

| Type | Description |
|------|-------------|
| `buckler` | Petit bouclier rond |
| `shield_round` | Bouclier rond |
| `shield_kite` | Bouclier en amande |
| `shield_tower` | Grand bouclier |
| `shield_crusader` | Bouclier de croisé |

---

## Head Gear

| Type | Description |
|------|-------------|
| `leather_cap` | Calotte de cuir |
| `chain_hood` | Capuche de mailles |
| `plate_helm` | Casque de plaques |
| `tiara` | Diadème |
| `crown_gold` | Couronne dorée |
| `hood` | Capuche |
| `hat_wizard` | Chapeau de mage |
| `bandana` | Bandana |
| `headband` | Bandeau |

---

## Capes

| Type | Description |
|------|-------------|
| `cape_solid` | Cape unie |
| `cape_tattered` | Cape déchirée |
| `cape_long` | Cape longue |

### Couleurs
- `red`, `blue`, `gray`, `black`, `white`, `green`, `purple`

---

## Accessories

| Type | Description |
|------|-------------|
| `necklace` | Collier |
| `ring` | Bague (stud) |
| `bracers` | Brassards |
| `shoulder_pads` | Épaulières |
| `belt` | Ceinture |
| `quiver` | Carquois |

---

## Structure des fichiers spritesheets

Les assets sont organisés dans le repo sous :
```
spritesheets/
├── body/
│   ├── male/
│   │   ├── light.png
│   │   ├── dark.png
│   │   └── ...
│   └── female/
│       └── ...
├── hair/
│   ├── bangs/
│   │   ├── black.png
│   │   └── ...
│   └── ...
├── torso/
│   ├── leather/
│   │   └── ...
│   └── ...
└── ...
```

**URL CDN pour charger les assets :**
```
https://raw.githubusercontent.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/master/spritesheets/{category}/{subcategory}/{variant}.png
```

## Pour explorer les assets

La meilleure façon de voir tous les assets disponibles est d'utiliser le générateur en ligne :
https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/

Il affiche toutes les catégories avec preview en temps réel.
