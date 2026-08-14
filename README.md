# Amber Run 3D

A remake of **Amber Run** as a new Godot 4.7 project. Same 2D sunset platformer — collect 5 coins, reach the flag, try not to fall — with every ColorRect swapped for a 3D asset rendered out of Blender.

## Play in a browser

GitHub Pages hosts both builds (first load is ~40 MB):

- Hub: https://masterbrogrammer.github.io/amber-run-3d/
- [Original (block art)](https://masterbrogrammer.github.io/amber-run-3d/original/)
- [3D remake](https://masterbrogrammer.github.io/amber-run-3d/remake/)

Click the game canvas once so it has keyboard focus.

Screenshots and grab-ready thumbs (full, card, OG, square) are in [`docs/thumbs/`](https://masterbrogrammer.github.io/amber-run-3d/thumbs/).

## Play locally

- **Editor:** open this folder in **Godot 4.7.1** and press **F5**.
- Original game (block art) lives in `../amber-run/`. This folder is the remake.

### Controls

- **A / D** or **arrows** — run
- **Space** or **W** — jump

Click the game window first so it has focus.

## Project layout

| Path | What |
|---|---|
| `main.tscn` | Game scene |
| `scripts/` | Player, coins, HUD (same feel as the original) |
| `audio/` | Jump / coin / fall / win SFX and the looping theme |
| `assets/` | Blender-rendered sprites |
| `blender/amber_assets.blend` | Source 3D scene used to render the sprites |

## Feel / tuning (kept from the original)

- Player speed `280`, jump `-620`, coyote `0.12s`, jump buffer `0.12s`
- Gravity is Godot default `980`
- Platforms are a shallow staircase (PlatA ~515, PlatB ~450, PlatC ~385, PlatD ~445)
- Fall below `y > 820` respawns
