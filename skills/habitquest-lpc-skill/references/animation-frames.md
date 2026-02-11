# Détails des frames d'animation LPC

Ce fichier décrit la disposition exacte des animations dans un spritesheet LPC universel.

## Structure du spritesheet universel

Dimensions : **832 × 1344 pixels** (13 colonnes × 21 lignes de frames 64×64)

```
Ligne  | Animation     | Direction | Frames | Colonnes utilisées
-------|---------------|-----------|--------|-------------------
  0    | Spellcast     | Haut      | 7      | 0-6
  1    | Spellcast     | Gauche    | 7      | 0-6
  2    | Spellcast     | Bas       | 7      | 0-6
  3    | Spellcast     | Droite    | 7      | 0-6
  4    | Thrust        | Haut      | 8      | 0-7
  5    | Thrust        | Gauche    | 8      | 0-7
  6    | Thrust        | Bas       | 8      | 0-7
  7    | Thrust        | Droite    | 8      | 0-7
  8    | Walk          | Haut      | 9      | 0-8
  9    | Walk          | Gauche    | 9      | 0-8
 10    | Walk          | Bas       | 9      | 0-8
 11    | Walk          | Droite    | 9      | 0-8
 12    | Slash         | Haut      | 6      | 0-5
 13    | Slash         | Gauche    | 6      | 0-5
 14    | Slash         | Bas       | 6      | 0-5
 15    | Slash         | Droite    | 6      | 0-5
 16    | Shoot         | Haut      | 13     | 0-12
 17    | Shoot         | Gauche    | 13     | 0-12
 18    | Shoot         | Bas       | 13     | 0-12
 19    | Shoot         | Droite    | 13     | 0-12
 20    | Hurt          | (toutes)  | 6      | 0-5
```

## Cycle d'animation recommandé

### Walk (marche)
- 9 frames, boucle continue
- Frame 0 = position neutre (idle)
- Cycle recommandé : 8 FPS (≈ 1.125s par cycle)

### Idle (repos)
- Utiliser la frame 0 du walk (startRow: 8, frame: 0)
- Ou animer lentement entre frames 0 et 1 du walk

### Spellcast (incantation)
- 7 frames, jouer une fois puis retour à idle
- Cycle recommandé : 10 FPS

### Thrust (estoc)
- 8 frames, jouer une fois puis retour à idle
- Cycle recommandé : 10 FPS

### Slash (frappe)
- 6 frames, jouer une fois puis retour à idle
- Cycle recommandé : 10 FPS

### Shoot (tir)
- 13 frames, jouer une fois puis retour à idle
- Cycle recommandé : 12 FPS

### Hurt (blessure)
- 6 frames, pas de direction (une seule ligne)
- Jouer une fois puis retour à idle
- Cycle recommandé : 6 FPS

## Animations LPCR/LPCE (si disponibles)

Les expansions ajoutent ces animations supplémentaires :
- **Run** — course rapide
- **Climb** — escalade
- **Jump** — saut
- **Bow** — révérence
- **Emotes** — expressions faciales

Ces animations ne sont pas dans le spritesheet standard 832×1344 et nécessitent
des feuilles séparées ou un sheet étendu.

## Formule de positionnement

Pour extraire la frame (col, row) du spritesheet :

```
sourceX = col × 64
sourceY = row × 64
```

Pour une animation donnée, direction donnée, frame N :
```
row = animation.startRow + directionOffset
col = N % animation.frames
sourceX = col × 64
sourceY = row × 64
```

Avec `directionOffset` : up=0, left=1, down=2, right=3

## Oversize frames

Certains assets (armes en particul) utilisent des frames plus grandes que 64×64,
typiquement 192×192 pour les armes oversize. Dans ce cas, le calcul change :

```
OVERSIZE_FRAME_W = 192
OVERSIZE_FRAME_H = 192
// Le personnage est centré dans la frame oversize
// Offset pour centrer : (192 - 64) / 2 = 64 pixels de marge
```

Les animations oversize courantes sont : slash et thrust avec des armes longues.
