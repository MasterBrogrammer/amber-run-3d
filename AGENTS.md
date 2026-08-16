# Amber Run 3D — project context

Remake of `../amber-run` as a **new** Godot 4.7.1 project. Same 2D scroller feel; visuals are Blender-rendered sprites instead of ColorRects.

Studio library (shared naming / Imagine / Hi3D): `/Users/stevenwoolery/studio/` — read `AGENTS.md` there before filing new art.

This file is for Grok / other agents. Read it before changing the game.

## What stays the same

- Collect **5 coins**, then touch the **flag** to win. Touching the flag early shows how many coins you got and offers restart.
- Fall below `y > 820` respawns the player.
- Controls: `ui_left` / `ui_right` to run, `ui_accept` / `ui_up` to jump.
- Player speed `280`, jump `-620`, coyote `0.12s`, jump buffer `0.12s`.
- Platform staircase: PlatA ~515, PlatB ~450, PlatC ~385, PlatD ~445.
- Audio: `audio/*.wav` copied from the original (theme −11 dB).

## What changed

- New folder: `/Users/stevenwoolery/amber-run-3d`
- Player is an `AnimatedSprite2D` (idle / run / jump) rendered from a 3D Blender character.
- Coins, platforms, ground, flag are PNG sprites from `blender/amber_assets.blend`.
- Sky is a rendered sunset plate plus two parallax hill layers (`assets/world/sky.png`, `hills_far.png`, `hills_near.png`).
- Ground includes a Blender-baked sunset shadow pass; soft decal blobs sit under each platform and the player.
- HUD text and win panel are reused for both the full clear and the early-flag result.
- Flag cloth uses `assets/world/flag_wave.gdshader`.

## Layout

| Path | Role |
|---|---|
| `main.tscn` | Scene |
| `scripts/player.gd` | Movement + animation state |
| `scripts/coin.gd` | Bobbing collectible |
| `scripts/game.gd` | Score, win, fall/respawn, music |
| `assets/` | Rendered sprites |
| `blender/amber_assets.blend` | Source 3D |

## Conventions

- Typed GDScript, Godot style (snake_case).
- Keep the demo small. Do not rewrite architecture unless asked.
- Re-render sprites from the blend file rather than painting over PNGs.
