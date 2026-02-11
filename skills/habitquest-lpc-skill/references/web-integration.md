# Guide d'intégration web — Patterns de code

Ce fichier contient les patterns de code pour chaque format de sortie supporté.
Chaque pattern est prêt à être personnalisé selon le personnage de l'utilisateur.

## Table des matières
1. [Format HTML5 Canvas](#html5-canvas)
2. [Format React/JSX](#reactjsx)
3. [Format CSS Sprite Animation](#css-sprite)
4. [Classe JS réutilisable](#canvas-class)
5. [Règles communes](#règles-communes)

---

## Règles communes

Quel que soit le format, TOUJOURS appliquer ces règles :

### Pixel-perfect rendering
```css
/* CSS — empêcher le lissage sur le sprite upscalé */
.sprite-container {
  image-rendering: pixelated;           /* Chrome, Edge */
  image-rendering: crisp-edges;         /* Firefox */
  -ms-interpolation-mode: nearest-neighbor; /* IE (legacy) */
}
```

```javascript
// Canvas — désactiver l'antialiasing
ctx.imageSmoothingEnabled = false;
ctx.mozImageSmoothingEnabled = false;
ctx.webkitImageSmoothingEnabled = false;
ctx.msImageSmoothingEnabled = false;
```

### Dimensions standard du spritesheet LPC
```javascript
const FRAME_WIDTH = 64;       // Largeur d'une frame
const FRAME_HEIGHT = 64;      // Hauteur d'une frame
const SHEET_COLS = 13;        // Nombre de colonnes dans le spritesheet universel
const SHEET_ROWS = 21;        // Nombre de lignes dans le spritesheet universel
const SHEET_WIDTH = 832;      // 13 × 64
const SHEET_HEIGHT = 1344;    // 21 × 64
```

### Map des animations (spritesheet universel LPC)
```javascript
const ANIMATIONS = {
  spellcast: { row: 0, frames: 7, directions: ['up', 'left', 'down', 'right'] },
  thrust:    { row: 4, frames: 8, directions: ['up', 'left', 'down', 'right'] },
  walk:      { row: 8, frames: 9, directions: ['up', 'left', 'down', 'right'] },
  slash:     { row: 12, frames: 6, directions: ['up', 'left', 'down', 'right'] },
  shoot:     { row: 16, frames: 13, directions: ['up', 'left', 'down', 'right'] },
  hurt:      { row: 20, frames: 6, directions: ['none'] }
};

// Chaque animation utilise N lignes consécutives (1 par direction)
// Direction order dans le sheet: up=0, left=1, down=2, right=3
const DIRECTION_OFFSET = { up: 0, left: 1, down: 2, right: 3 };
```

---

## HTML5 Canvas

Pattern pour une page HTML autonome avec animation Canvas.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{CHARACTER_NAME}}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: {{BACKGROUND_COLOR}};
      font-family: 'Courier New', monospace;
    }
    canvas {
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }
    .controls {
      margin-top: 16px;
      display: flex;
      gap: 8px;
    }
    .controls button {
      padding: 8px 16px;
      font-family: inherit;
      font-size: 14px;
      cursor: pointer;
      border: 2px solid #333;
      background: #fff;
      border-radius: 4px;
    }
    .controls button.active {
      background: #333;
      color: #fff;
    }
  </style>
</head>
<body>
  <canvas id="spriteCanvas" width="{{DISPLAY_SIZE}}" height="{{DISPLAY_SIZE}}"></canvas>
  <div class="controls">
    <button data-anim="walk" class="active">Walk</button>
    <button data-anim="idle">Idle</button>
    <button data-anim="slash">Attack</button>
    <button data-anim="spellcast">Cast</button>
    <button data-anim="hurt">Hurt</button>
  </div>
  <div class="controls">
    <button data-dir="up">↑</button>
    <button data-dir="left">←</button>
    <button data-dir="down" class="active">↓</button>
    <button data-dir="right">→</button>
  </div>

  <script>
    const canvas = document.getElementById('spriteCanvas');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    const FRAME_W = 64;
    const FRAME_H = 64;
    const SCALE = {{SCALE}};
    const DISPLAY = FRAME_W * SCALE;

    // Animation map — adapter selon le spritesheet
    const ANIMS = {
      spellcast: { startRow: 0,  frames: 7 },
      thrust:    { startRow: 4,  frames: 8 },
      walk:      { startRow: 8,  frames: 9 },
      slash:     { startRow: 12, frames: 6 },
      shoot:     { startRow: 16, frames: 13 },
      hurt:      { startRow: 20, frames: 6 }
    };

    // idle = walk frame 0 (statique)
    ANIMS.idle = { startRow: 8, frames: 1 };

    const DIR_OFFSET = { up: 0, left: 1, down: 2, right: 3 };

    let currentAnim = 'walk';
    let currentDir = 'down';
    let frameIndex = 0;
    let tickCount = 0;
    const TICKS_PER_FRAME = 8; // Vitesse d'animation (plus haut = plus lent)

    // Charger le spritesheet
    const sprite = new Image();
    sprite.src = '{{SPRITESHEET_URL}}';
    sprite.onload = () => requestAnimationFrame(gameLoop);

    function gameLoop() {
      tickCount++;
      if (tickCount >= TICKS_PER_FRAME) {
        tickCount = 0;
        const anim = ANIMS[currentAnim];
        frameIndex = (frameIndex + 1) % anim.frames;
      }
      render();
      requestAnimationFrame(gameLoop);
    }

    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const anim = ANIMS[currentAnim];
      const row = anim.startRow + (currentAnim === 'hurt' ? 0 : DIR_OFFSET[currentDir]);
      const sx = frameIndex * FRAME_W;
      const sy = row * FRAME_H;
      ctx.drawImage(sprite, sx, sy, FRAME_W, FRAME_H, 0, 0, DISPLAY, DISPLAY);
    }

    // Contrôles
    document.querySelectorAll('[data-anim]').forEach(btn => {
      btn.addEventListener('click', () => {
        currentAnim = btn.dataset.anim;
        frameIndex = 0;
        document.querySelectorAll('[data-anim]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    document.querySelectorAll('[data-dir]').forEach(btn => {
      btn.addEventListener('click', () => {
        currentDir = btn.dataset.dir;
        document.querySelectorAll('[data-dir]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    // Contrôle clavier
    document.addEventListener('keydown', (e) => {
      const keyMap = {
        ArrowUp: 'up', ArrowDown: 'down',
        ArrowLeft: 'left', ArrowRight: 'right'
      };
      if (keyMap[e.key]) {
        currentDir = keyMap[e.key];
        if (currentAnim === 'idle') currentAnim = 'walk';
        document.querySelectorAll('[data-dir]').forEach(b => b.classList.remove('active'));
        document.querySelector(`[data-dir="${keyMap[e.key]}"]`)?.classList.add('active');
      }
    });
  </script>

  <!-- CREDITS LPC — OBLIGATOIRE -->
  <!-- {{CREDITS_SECTION}} -->
</body>
</html>
```

**Variables à remplacer :**
- `{{CHARACTER_NAME}}` — Nom du personnage
- `{{BACKGROUND_COLOR}}` — Couleur de fond (ex: `#1a1a2e`)
- `{{DISPLAY_SIZE}}` — Taille canvas en px (ex: `128`)
- `{{SCALE}}` — Facteur de scale (ex: `2` pour 128px depuis 64px)
- `{{SPRITESHEET_URL}}` — URL ou chemin vers le spritesheet PNG
- `{{CREDITS_SECTION}}` — Bloc de crédits LPC

---

## React/JSX

Pattern pour un composant React avec hooks.

```jsx
import { useState, useEffect, useRef, useCallback } from 'react';

const FRAME_W = 64;
const FRAME_H = 64;

const ANIMS = {
  spellcast: { startRow: 0, frames: 7 },
  thrust: { startRow: 4, frames: 8 },
  walk: { startRow: 8, frames: 9 },
  slash: { startRow: 12, frames: 6 },
  shoot: { startRow: 16, frames: 13 },
  hurt: { startRow: 20, frames: 6 },
  idle: { startRow: 8, frames: 1 }
};

const DIR_OFFSET = { up: 0, left: 1, down: 2, right: 3 };

export default function LPCCharacter({
  spriteSheetUrl = '{{SPRITESHEET_URL}}',
  scale = {{SCALE}},
  initialAnim = 'walk',
  initialDir = 'down',
  fps = 8,
  showControls = true
}) {
  const canvasRef = useRef(null);
  const spriteRef = useRef(null);
  const frameRef = useRef(0);
  const [anim, setAnim] = useState(initialAnim);
  const [dir, setDir] = useState(initialDir);
  const [loaded, setLoaded] = useState(false);

  const displaySize = FRAME_W * scale;

  // Charger le sprite
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => { spriteRef.current = img; setLoaded(true); };
    img.src = spriteSheetUrl;
  }, [spriteSheetUrl]);

  // Reset frame quand l'animation change
  useEffect(() => { frameRef.current = 0; }, [anim]);

  // Boucle d'animation
  useEffect(() => {
    if (!loaded) return;
    let animId;
    let tick = 0;
    const ticksPerFrame = Math.round(60 / fps);

    const loop = () => {
      tick++;
      if (tick >= ticksPerFrame) {
        tick = 0;
        const a = ANIMS[anim];
        frameRef.current = (frameRef.current + 1) % a.frames;
      }
      draw();
      animId = requestAnimationFrame(loop);
    };

    const draw = () => {
      const canvas = canvasRef.current;
      if (!canvas || !spriteRef.current) return;
      const ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, displaySize, displaySize);

      const a = ANIMS[anim];
      const row = a.startRow + (anim === 'hurt' ? 0 : DIR_OFFSET[dir]);
      const sx = frameRef.current * FRAME_W;
      const sy = row * FRAME_H;
      ctx.drawImage(spriteRef.current, sx, sy, FRAME_W, FRAME_H, 0, 0, displaySize, displaySize);
    };

    animId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animId);
  }, [loaded, anim, dir, fps, displaySize]);

  const animButtons = ['walk', 'idle', 'slash', 'spellcast', 'hurt'];
  const dirButtons = [
    { key: 'up', label: '↑' },
    { key: 'left', label: '←' },
    { key: 'down', label: '↓' },
    { key: 'right', label: '→' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <canvas
        ref={canvasRef}
        width={displaySize}
        height={displaySize}
        style={{ imageRendering: 'pixelated' }}
      />
      {showControls && (
        <>
          <div style={{ display: 'flex', gap: 4 }}>
            {animButtons.map(a => (
              <button
                key={a}
                onClick={() => setAnim(a)}
                style={{
                  padding: '4px 10px', cursor: 'pointer',
                  background: anim === a ? '#333' : '#fff',
                  color: anim === a ? '#fff' : '#333',
                  border: '2px solid #333', borderRadius: 4,
                  fontFamily: 'monospace', fontSize: 12
                }}
              >
                {a}
              </button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 4 }}>
            {dirButtons.map(d => (
              <button
                key={d.key}
                onClick={() => setDir(d.key)}
                style={{
                  padding: '4px 10px', cursor: 'pointer',
                  background: dir === d.key ? '#333' : '#fff',
                  color: dir === d.key ? '#fff' : '#333',
                  border: '2px solid #333', borderRadius: 4,
                  fontFamily: 'monospace', fontSize: 14
                }}
              >
                {d.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
```

---

## CSS Sprite

Pattern pour animation CSS pure avec `steps()`. Idéal pour les cas simples (walk loop).

```html
<style>
  .lpc-sprite {
    width: {{DISPLAY_SIZE}}px;
    height: {{DISPLAY_SIZE}}px;
    background-image: url('{{SPRITESHEET_URL}}');
    background-size: {{SHEET_SCALED_W}}px {{SHEET_SCALED_H}}px;
    background-repeat: no-repeat;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    animation: lpc-walk {{ANIM_DURATION}}s steps({{FRAME_COUNT}}) infinite;
    /* Position initiale : walk-down, frame 0 */
    background-position: 0px -{{WALK_DOWN_Y}}px;
  }

  @keyframes lpc-walk {
    from { background-position-x: 0; }
    to   { background-position-x: -{{TOTAL_FRAMES_WIDTH}}px; }
  }

  /* Classes utilitaires pour changer direction */
  .lpc-sprite.dir-up    { background-position-y: -{{WALK_UP_Y}}px; }
  .lpc-sprite.dir-left  { background-position-y: -{{WALK_LEFT_Y}}px; }
  .lpc-sprite.dir-down  { background-position-y: -{{WALK_DOWN_Y}}px; }
  .lpc-sprite.dir-right { background-position-y: -{{WALK_RIGHT_Y}}px; }
</style>

<div class="lpc-sprite dir-down"></div>
```

**Calcul des variables CSS sprite :**
```
SCALE = display_size / 64
SHEET_SCALED_W = 832 * SCALE
SHEET_SCALED_H = 1344 * SCALE
WALK_UP_Y    = 8 * 64 * SCALE  (row 8)
WALK_LEFT_Y  = 9 * 64 * SCALE  (row 9)
WALK_DOWN_Y  = 10 * 64 * SCALE (row 10)
WALK_RIGHT_Y = 11 * 64 * SCALE (row 11)
FRAME_COUNT  = 9 (walk frames)
TOTAL_FRAMES_WIDTH = 9 * 64 * SCALE
ANIM_DURATION = 9 / 8 = 1.125 (9 frames à 8fps)
```

---

## Canvas Class

Classe JS réutilisable pour intégration dans un projet existant.

```javascript
class LPCSprite {
  constructor(options = {}) {
    this.spriteUrl = options.spriteUrl || '';
    this.frameW = options.frameW || 64;
    this.frameH = options.frameH || 64;
    this.scale = options.scale || 2;
    this.fps = options.fps || 8;
    this.x = options.x || 0;
    this.y = options.y || 0;

    this.animations = options.animations || {
      spellcast: { startRow: 0, frames: 7 },
      thrust: { startRow: 4, frames: 8 },
      walk: { startRow: 8, frames: 9 },
      slash: { startRow: 12, frames: 6 },
      shoot: { startRow: 16, frames: 13 },
      hurt: { startRow: 20, frames: 6 },
      idle: { startRow: 8, frames: 1 }
    };

    this.dirOffset = { up: 0, left: 1, down: 2, right: 3 };

    this.currentAnim = 'idle';
    this.currentDir = 'down';
    this.frameIndex = 0;
    this.tickCount = 0;
    this.ticksPerFrame = Math.round(60 / this.fps);

    this.image = null;
    this.loaded = false;
    this._loadImage();
  }

  _loadImage() {
    this.image = new Image();
    this.image.crossOrigin = 'anonymous';
    this.image.onload = () => { this.loaded = true; };
    this.image.src = this.spriteUrl;
  }

  setAnimation(name) {
    if (this.currentAnim !== name) {
      this.currentAnim = name;
      this.frameIndex = 0;
      this.tickCount = 0;
    }
  }

  setDirection(dir) {
    this.currentDir = dir;
  }

  update() {
    if (!this.loaded) return;
    this.tickCount++;
    if (this.tickCount >= this.ticksPerFrame) {
      this.tickCount = 0;
      const anim = this.animations[this.currentAnim];
      if (anim) {
        this.frameIndex = (this.frameIndex + 1) % anim.frames;
      }
    }
  }

  draw(ctx) {
    if (!this.loaded || !this.image) return;
    ctx.imageSmoothingEnabled = false;

    const anim = this.animations[this.currentAnim];
    if (!anim) return;

    const row = anim.startRow +
      (this.currentAnim === 'hurt' ? 0 : (this.dirOffset[this.currentDir] || 0));

    const sx = this.frameIndex * this.frameW;
    const sy = row * this.frameH;
    const dw = this.frameW * this.scale;
    const dh = this.frameH * this.scale;

    ctx.drawImage(
      this.image,
      sx, sy, this.frameW, this.frameH,
      this.x, this.y, dw, dh
    );
  }

  get displayWidth() { return this.frameW * this.scale; }
  get displayHeight() { return this.frameH * this.scale; }
}
```

**Utilisation :**
```javascript
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const hero = new LPCSprite({
  spriteUrl: 'hero-spritesheet.png',
  scale: 2,
  x: 100,
  y: 100
});

hero.setAnimation('walk');
hero.setDirection('down');

function gameLoop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  hero.update();
  hero.draw(ctx);
  requestAnimationFrame(gameLoop);
}

gameLoop();
```

---

## Multi-layer compositing

Si on charge les layers séparément (body + hair + armor...) :

```javascript
async function composeLayers(layerUrls, frameW = 64, frameH = 64) {
  // Charger toutes les images
  const images = await Promise.all(
    layerUrls.map(url => new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    }))
  );

  // Créer un canvas composite
  const width = images[0].width;
  const height = images[0].height;
  const offscreen = document.createElement('canvas');
  offscreen.width = width;
  offscreen.height = height;
  const ctx = offscreen.getContext('2d');

  // Superposer les layers dans l'ordre
  images.forEach(img => {
    ctx.drawImage(img, 0, 0);
  });

  return offscreen;
}
```
