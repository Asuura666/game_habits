"use client";

import { useRef, useEffect, useCallback } from 'react';
import {
  LPC_ANIMATIONS,
  LPC_DIRECTION_OFFSET,
  LPC_FRAME_SIZE,
  type SpriteAnimation,
  type SpriteDirection,
} from '@/types/character';

interface UseSpriteAnimationOptions {
  spriteSheetUrl: string | null;
  animation?: SpriteAnimation;
  direction?: SpriteDirection;
  scale?: number;
  fps?: number;
  paused?: boolean;
  onAnimationComplete?: () => void;
}

export function useSpriteAnimation({
  spriteSheetUrl,
  animation = 'idle',
  direction = 'down',
  scale = 2,
  fps = 8,
  paused = false,
  onAnimationComplete,
}: UseSpriteAnimationOptions) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const spriteRef = useRef<HTMLImageElement | null>(null);
  const frameRef = useRef(0);
  const lastFrameTimeRef = useRef(0);
  const animRef = useRef(animation);
  const dirRef = useRef(direction);
  const pausedRef = useRef(paused);

  useEffect(() => { pausedRef.current = paused; }, [paused]);
  useEffect(() => { animRef.current = animation; frameRef.current = 0; }, [animation]);
  useEffect(() => { dirRef.current = direction; }, [direction]);

  // Load sprite
  useEffect(() => {
    if (!spriteSheetUrl) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => { spriteRef.current = img; };
    img.src = spriteSheetUrl;
  }, [spriteSheetUrl]);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const displaySize = LPC_FRAME_SIZE * scale;
    canvas.width = displaySize;
    canvas.height = displaySize;

    const frameInterval = 1000 / fps;
    let animId: number;

    const render = (timestamp: number) => {
      animId = requestAnimationFrame(render);
      if (!spriteRef.current) return;

      if (!pausedRef.current && timestamp - lastFrameTimeRef.current >= frameInterval) {
        lastFrameTimeRef.current = timestamp;
        const anim = LPC_ANIMATIONS[animRef.current];
        frameRef.current = (frameRef.current + 1) % anim.frames;
        if (frameRef.current === 0) onAnimationComplete?.();
      }

      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, displaySize, displaySize);

      const anim = LPC_ANIMATIONS[animRef.current];
      const dirOffset = animRef.current === 'hurt' ? 0 : LPC_DIRECTION_OFFSET[dirRef.current];
      const row = anim.startRow + dirOffset;
      const sx = frameRef.current * LPC_FRAME_SIZE;
      const sy = row * LPC_FRAME_SIZE;

      ctx.drawImage(spriteRef.current, sx, sy, LPC_FRAME_SIZE, LPC_FRAME_SIZE, 0, 0, displaySize, displaySize);
    };

    animId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animId);
  }, [scale, fps, onAnimationComplete]);

  return canvasRef;
}
