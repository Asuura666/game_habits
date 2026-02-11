# Guide Personnages SVG / CSS (Alternative non-LPC)

Si l'utilisateur ne veut pas du style pixel-art LPC mais un personnage en style moderne,
vectoriel ou illustratif, utilise cette approche.

## Quand utiliser cette approche ?

- L'utilisateur dit "pas de pixel art", "style moderne", "flat design", "illustré"
- Le personnage est destiné à un site corporate, une landing page, une mascotte
- L'utilisateur veut un avatar, une illustration, pas un sprite de jeu
- Le contexte est non-gaming (site web, app, présentation)

## Techniques SVG pour personnages

### Structure d'un personnage SVG modulaire

```svg
<svg viewBox="0 0 200 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Groupes nommés pour chaque partie du corps -->
  <g id="character" transform="translate(100, 200)">
    <!-- Layers de bas en haut -->
    <g id="legs">...</g>
    <g id="torso">...</g>
    <g id="arms">...</g>
    <g id="head">
      <g id="face">...</g>
      <g id="hair">...</g>
      <g id="accessories">...</g>
    </g>
  </g>
</svg>
```

### Animations SVG avec CSS

```css
/* Animation de marche par rotation des jambes */
#left-leg { animation: walk-left 0.6s ease-in-out infinite alternate; }
#right-leg { animation: walk-right 0.6s ease-in-out infinite alternate; }

@keyframes walk-left {
  from { transform: rotate(-15deg); }
  to   { transform: rotate(15deg); }
}
@keyframes walk-right {
  from { transform: rotate(15deg); }
  to   { transform: rotate(-15deg); }
}

/* Blink (clignement) */
#eyelids {
  animation: blink 3s ease-in-out infinite;
}
@keyframes blink {
  0%, 90%, 100% { transform: scaleY(1); }
  95%           { transform: scaleY(0.1); }
}

/* Respiration */
#torso {
  animation: breathe 2s ease-in-out infinite;
  transform-origin: bottom center;
}
@keyframes breathe {
  0%, 100% { transform: scaleY(1); }
  50%      { transform: scaleY(1.02); }
}
```

### Personnages CSS pur (CSS Art)

Pour des personnages simples, le CSS art utilise des divs et pseudo-éléments :

```css
.character {
  position: relative;
  width: 100px;
  height: 200px;
}
.character .head {
  width: 60px; height: 60px;
  background: #ffd5a0;
  border-radius: 50%;
  position: absolute;
  top: 0; left: 20px;
}
.character .body {
  width: 70px; height: 80px;
  background: #4a90d9;
  border-radius: 10px;
  position: absolute;
  top: 55px; left: 15px;
}
/* etc. */
```

## Approche React pour personnages interactifs

```jsx
function SVGCharacter({ skinColor, hairColor, hairStyle, outfit, expression }) {
  return (
    <svg viewBox="0 0 200 400" style={{ width: '200px' }}>
      {/* Body */}
      <ellipse cx="100" cy="250" rx="35" ry="55" fill={outfit.color} />
      {/* Head */}
      <circle cx="100" cy="150" r="40" fill={skinColor} />
      {/* Eyes */}
      <circle cx="85" cy="145" r="5" fill="white" />
      <circle cx="115" cy="145" r="5" fill="white" />
      <circle cx="87" cy="145" r="3" fill="#333" />
      <circle cx="117" cy="145" r="3" fill="#333" />
      {/* Hair - dynamique selon le style */}
      <HairComponent style={hairStyle} color={hairColor} />
      {/* Expression */}
      <ExpressionComponent type={expression} />
    </svg>
  );
}
```

## Quand recommander LPC vs SVG

| Critère | LPC (pixel art) | SVG (vectoriel) |
|---------|-----------------|-----------------|
| Style | Rétro, gaming, pixel | Moderne, clean, corporate |
| Animation | Spritesheet frames | CSS/JS transforms |
| Scalabilité | Upscale pixelated | Infiniment scalable |
| Personnalisation | Assets prédéfinis | Totalement libre |
| Temps de création | Rapide (générateur) | Plus long (dessin) |
| Performance | Léger (1 image) | Variable |
| Intégration web | Canvas / CSS sprite | SVG inline / img |

Si l'utilisateur hésite, propose les deux approches et laisse-le choisir.
