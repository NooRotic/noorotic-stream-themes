# NooRotic Stream Themes

Custom lower third templates for [VinciFlow](https://github.com/mmlTools/vinci-flow) — a broadcast-grade stream graphics controller for OBS Studio.

## Themes

| Theme | Style | Animated | Avatar |
|---|---|---|---|
| `network-bar` | CNN/Fox-style bottom bar, cyberpunk matrix palette | - | No |
| `anchor-card` | Dark card with avatar circle and left color stripe | - | Yes |
| `corporate-clean` | Light card, shadow, bottom accent gradient | - | Yes |
| `breaking-news` | Red pulsing BREAKING badge, high contrast | Pulse | No |
| `lower-doc` | Documentary dark bar, large title, fade-out rule | - | No |
| `breaking-bowltv` | BowlTV-branded breaking news with logo | Pulse | No |
| `neon-pulse` | Glowing border, breathing drop-shadows, neon flicker | Heavy | No |
| `tiedye-trip` | Psychedelic tie-dye swirl, rainbow text, color cycling | Heavy | No |
| `headline-ticker` | Auto-cycling headlines, orbiting glow, LIVE badge | Heavy | No |

## Installation

1. Download or clone this repo
2. Copy any theme folder from `themes/` into your VinciFlow themes directory:
   - Default location: `C:\Program Files\obs-studio\data\themes\`
   - Or wherever your OBS portable install lives: `<OBS>/data/themes/`
3. Restart OBS or reload VinciFlow from the dock

## Theme Structure

Each theme contains three files:

```
theme-name/
  template.html   # HTML fragment (goes inside <li id="{{ID}}">)
  template.css    # Styles scoped to #{{ID}}
  template.json   # Metadata + default values
```

## Live Data

Templates support live data injection via VinciFlow's parameter system. Write JSON to `parameters_lt_<ID>.json` and bind with `data-` attributes:

```html
<span data-score></span>
<span data-player></span>
```

The `headline-ticker` theme demonstrates JS-driven headline rotation — feed pipe-separated headlines:
```json
{ "headlines": "First headline|Second headline|Third" }
```

## Placeholders

All templates use VinciFlow's placeholder system:

| Placeholder | Purpose |
|---|---|
| `{{ID}}` | Unique lower third ID |
| `{{TITLE}}` | Main title text |
| `{{SUBTITLE}}` | Subtitle text |
| `{{PROFILE_PICTURE_URL}}` | Avatar image URL |
| `{{PRIMARY_COLOR}}` | Primary accent color |
| `{{SECONDARY_COLOR}}` | Secondary accent color |
| `{{TITLE_COLOR}}` / `{{SUBTITLE_COLOR}}` | Text colors |
| `{{OPACITY}}` | Background opacity (0-100) |
| `{{RADIUS}}` | Border radius in px |
| `{{FONT_FAMILY}}` | Font family name |
| `{{TITLE_SIZE}}` / `{{SUBTITLE_SIZE}}` | Font sizes in px |
| `{{AVATAR_WIDTH}}` / `{{AVATAR_HEIGHT}}` | Avatar dimensions |
| `{{ANIM_IN}}` / `{{ANIM_OUT}}` | animate.css class names |

## License

MIT
