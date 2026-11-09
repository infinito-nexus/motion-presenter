# Theme contract

A theme is one stylesheet and one logo. The skill ships a neutral default (`defaults/theme/film.css`, `defaults/theme/logo.svg`); a project brings its own by writing the same tokens. Nothing in the scene library names a colour or a font: it reads these tokens.

## Tokens

Set on `:root` in the film's `src/film.css`.

| Token | Role | Default |
|---|---|---|
| `--bg` | canvas | `#111316` |
| `--bg2` | raised surface: cards, tiles, terminal bars | `#1B1E23` |
| `--ink` | main text and strokes | `#F1F1EE` |
| `--ink2` | secondary text | `#B3B7BD` |
| `--ink3` | muted text, idle dots, hints | `#6F757D` |
| `--accent` | filled accent: check circles, highlight rows | `#2C6E68` |
| `--accent2` | bright accent: kickers, rings, routes, underlines | `#4FB5AA` |
| `--sans` | display and body font stack | `"DejaVu Sans", system-ui, sans-serif` |
| `--mono` | monospace font stack | `"DejaVu Sans Mono", ui-monospace, monospace` |

`--hair` (hairlines) is derived from `--ink` in the default stylesheet; a theme may set it, it does not have to. Tints, glows and overlays in the scenes are `color-mix()` of these tokens, so a new palette recolours every scene.

## Logo

The logo is a path, packed into the film as `ASSETS.img.logo`:

```bash
python3 <SKILL_DIR>/scripts/assets.py <film>/src/assets.js --img logo=<logo file> --font "<Family>:<weight>=<font file>"
```

PNG, JPEG and SVG work. The default is `defaults/theme/logo.svg`. Scenes draw it round (`border-radius: 50%`), so a square logo with some margin reads best.

## A project theme

1. Copy `defaults/theme/film.css` over the film's `src/film.css` (or the series' shared copy).
2. Replace the nine tokens; keep the class names below `:root`.
3. Pack the logo and the fonts the tokens name with `assets.py`, then render.

A generator (for example a design system that writes the tokens from its own palette) writes exactly this `:root` block and passes the logo path; nothing generated belongs in this repository.
