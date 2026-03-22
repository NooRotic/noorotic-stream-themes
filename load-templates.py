#!/usr/bin/env python3
"""
VinciFlow Template Loader
Injects all theme templates into lt-state.json with pre-configured text and branding.
Run this, then restart OBS (or call ReloadFromDisk via WebSocket).

Usage:
  python3 load-templates.py <path-to-lt-state.json>
  python3 load-templates.py   (auto-detects common OBS locations)
"""

import json
import os
import sys
import uuid
import shutil
from datetime import datetime

# ─── Stream Branding Defaults ───────────────────────────────────────
BRAND = {
    "primary_color": "#00ff88",
    "secondary_color": "#0a0a0a",
    "title_color": "#f9fafb",
    "subtitle_color": "#cccccc",
    "font_family": "Orbitron",
    "title": "NooRotic",
    "subtitle": "Live Stream",
}

# ─── Template Definitions ───────────────────────────────────────────
# Each entry: (slug, label, title, subtitle, overrides)
# overrides replace the defaults from template.json

TEMPLATES = [
    # Button themes
    ("network-bar", "LT: Network Bar", "NooRotic", "Live Now", {
        "lt_position": "lt-pos-bottom-left",
    }),
    ("anchor-card", "LT: Anchor Card", "NooRotic", "Streamer & Creator", {
        "primary_color": "#3b82f6",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("corporate-clean", "LT: Corporate Clean", "NooRotic", "Presented by NooRotic", {
        "primary_color": "#2563eb",
        "secondary_color": "#7c3aed",
        "title_color": "#111827",
        "subtitle_color": "#6b7280",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("breaking-news", "LT: Breaking News", "Breaking Update", "Details incoming", {
        "primary_color": "#dc2626",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("lower-doc", "LT: Documentary", "NooRotic", "A deeper look", {
        "primary_color": "#d4a574",
        "font_family": "Georgia",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("breaking-bowltv", "LT: BowlTV Breaking", "Perfect Game Alert", "Live from the lanes", {
        "primary_color": "#51BFE2",
        "secondary_color": "#368096",
        "title_color": "#FFF2F2",
        "subtitle_color": "#CCC2C2",
        "font_family": "Montserrat",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("neon-pulse", "LT: Neon Pulse", "NooRotic", "Stream Online", {
        "secondary_color": "#00bfff",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("tiedye-trip", "LT: Tie-Dye Trip", "Good Vibes Only", "Peace Love Stream", {
        "primary_color": "#ff006e",
        "secondary_color": "#8338ec",
        "font_family": "Fredoka",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("headline-ticker", "LT: Headline Ticker", "NooRotic Live", "Streaming now", {
        "font_family": "Inter",
        "lt_position": "lt-pos-bottom-left",
    }),

    # Specialty themes
    ("scoreboard", "LT: Scoreboard", "NooRotic", "vs Opponent", {
        "lt_position": "lt-pos-bottom-center",
    }),
    ("poll-results", "LT: Poll Results", "What should we play?", "Vote in chat!", {
        "primary_color": "#00ff88",
        "secondary_color": "#3b82f6",
        "font_family": "Inter",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("countdown", "LT: Countdown", "Stream Starts In", "Get ready!", {
        "secondary_color": "#00bfff",
        "lt_position": "lt-pos-bottom-center",
    }),

    # Wide themes
    ("network-bar-wide", "LT: Network Bar Wide", "NooRotic", "Live Stream", {
        "lt_position": "lt-pos-bottom-left",
    }),
    ("anchor-card-wide", "LT: Anchor Card Wide", "NooRotic", "Streamer & Creator", {
        "primary_color": "#3b82f6",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("corporate-clean-wide", "LT: Corporate Wide", "NooRotic", "Webinar in progress", {
        "primary_color": "#2563eb",
        "secondary_color": "#7c3aed",
        "title_color": "#111827",
        "subtitle_color": "#6b7280",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("breaking-news-wide", "LT: Breaking News Wide", "Breaking Update", "Details incoming", {
        "primary_color": "#dc2626",
        "font_family": "Segoe UI",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("lower-doc-wide", "LT: Documentary Wide", "NooRotic", "A deeper look", {
        "primary_color": "#d4a574",
        "font_family": "Georgia",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("breaking-bowltv-wide", "LT: BowlTV Wide", "Perfect Game Alert", "Live from the lanes", {
        "primary_color": "#51BFE2",
        "secondary_color": "#368096",
        "title_color": "#FFF2F2",
        "subtitle_color": "#CCC2C2",
        "font_family": "Montserrat",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("neon-pulse-wide", "LT: Neon Pulse Wide", "NooRotic", "Stream Online", {
        "secondary_color": "#00bfff",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("tiedye-trip-wide", "LT: Tie-Dye Wide", "Good Vibes Only", "Peace Love Stream", {
        "primary_color": "#ff006e",
        "secondary_color": "#8338ec",
        "font_family": "Fredoka",
        "lt_position": "lt-pos-bottom-left",
    }),
    ("headline-ticker-wide", "LT: Ticker Wide", "NooRotic Live", "Streaming now", {
        "font_family": "Inter",
        "lt_position": "lt-pos-bottom-left",
    }),
]


def gen_id():
    """Generate a VinciFlow-style ID."""
    return "lt_" + uuid.uuid4().hex


def read_template_files(sources_dir, slug):
    """Read template.html, template.css, template.json, and optional template.js."""
    base = os.path.join(sources_dir, slug)
    result = {}

    html_path = os.path.join(base, "template.html")
    css_path = os.path.join(base, "template.css")
    json_path = os.path.join(base, "template.json")
    js_path = os.path.join(base, "template.js")

    if not os.path.isfile(html_path):
        return None

    with open(html_path, "r", encoding="utf-8") as f:
        result["html"] = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        result["css"] = f.read()
    with open(json_path, "r", encoding="utf-8") as f:
        result["meta"] = json.load(f)

    # Split out <script> tags from HTML into js_template
    html = result["html"]
    js = ""
    if "<script>" in html:
        import re
        scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
        js = "\n".join(scripts)
        html = re.sub(r"\s*<script>.*?</script>\s*", "\n", html, flags=re.DOTALL)
        result["html"] = html.strip()

    if os.path.isfile(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

    result["js"] = js
    return result


def build_item(slug, label, title, subtitle, overrides, templates):
    """Build a single lt-state.json item entry."""
    tpl = templates.get(slug)
    if not tpl:
        print(f"  SKIP  {slug} (template files not found)")
        return None

    meta_defaults = tpl["meta"].get("defaults", {})

    # Start with VinciFlow's base defaults
    item = {
        "id": gen_id(),
        "label": label,
        "title": title,
        "subtitle": subtitle,
        "html_template": tpl["html"],
        "css_template": tpl["css"],
        "js_template": tpl["js"],
        "profile_picture": "",
        "anim_in": meta_defaults.get("ANIM_IN", "animate__fadeInUp"),
        "anim_in_sound": "",
        "anim_out": meta_defaults.get("ANIM_OUT", "animate__fadeOutDown"),
        "anim_out_sound": "",
        "api_bridge_enabled": True,
        "api_template": "",
        "avatar_height": int(meta_defaults.get("AVATAR_HEIGHT", 100)),
        "avatar_width": int(meta_defaults.get("AVATAR_WIDTH", 100)),
        "bg_color": "#111827",
        "font_family": BRAND["font_family"],
        "hotkey": "",
        "lt_position": "lt-pos-bottom-left",
        "opacity": int(meta_defaults.get("OPACITY", 85)),
        "order": 0,
        "primary_color": BRAND["primary_color"],
        "radius": int(meta_defaults.get("RADIUS", 5)),
        "repeat_every_sec": 0,
        "repeat_visible_sec": 0,
        "secondary_color": BRAND["secondary_color"],
        "subtitle_color": BRAND["subtitle_color"],
        "subtitle_size": int(meta_defaults.get("SUBTITLE_SIZE", 24)),
        "text_color": BRAND["title_color"],
        "title_color": BRAND["title_color"],
        "title_size": int(meta_defaults.get("TITLE_SIZE", 46)),
    }

    # Apply per-template overrides
    for k, v in overrides.items():
        item[k] = v

    return item


def find_state_file():
    """Try to auto-detect lt-state.json location."""
    candidates = [
        # Common portable OBS locations
        r"/mnt/c/OBS/obs-studio/data/themes/default/lt-state.json",
        r"C:\OBS\obs-studio\data\themes\default\lt-state.json",
        # Default OBS install
        r"C:\Program Files\obs-studio\data\themes\default\lt-state.json",
        r"/mnt/c/Program Files/obs-studio/data/themes/default/lt-state.json",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def main():
    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sources_dir = os.path.join(script_dir, "template_sources")

    if not os.path.isdir(sources_dir):
        print(f"Error: {sources_dir} not found. Run from repo root.")
        sys.exit(1)

    # Find lt-state.json
    if len(sys.argv) > 1:
        state_path = sys.argv[1]
    else:
        state_path = find_state_file()

    if not state_path or not os.path.isfile(state_path):
        print("Error: Could not find lt-state.json")
        print("Usage: python3 load-templates.py <path-to-lt-state.json>")
        print("  e.g. python3 load-templates.py /mnt/c/OBS/obs-studio/data/themes/default/lt-state.json")
        sys.exit(1)

    print(f"State file: {state_path}")
    print(f"Sources:    {sources_dir}")
    print()

    # Backup
    backup = state_path + f".backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(state_path, backup)
    print(f"Backup:     {backup}")
    print()

    # Load current state
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Read all template source files
    print("Reading template sources...")
    templates = {}
    for slug, *_ in TEMPLATES:
        tpl = read_template_files(sources_dir, slug)
        if tpl:
            templates[slug] = tpl

    print(f"  Found {len(templates)} of {len(TEMPLATES)} templates")
    print()

    # Track existing template labels to avoid duplicates
    existing_labels = {item.get("label", "") for item in state.get("items", [])}

    # Build new items
    print("Injecting templates...")
    added = 0
    skipped = 0
    for slug, label, title, subtitle, overrides in TEMPLATES:
        if label in existing_labels:
            print(f"  EXISTS {label} (skipping)")
            skipped += 1
            continue

        item = build_item(slug, label, title, subtitle, overrides, templates)
        if item:
            state["items"].append(item)
            print(f"  ADD    {label}")
            added += 1

    # Write updated state
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

    print()
    print(f"Done! Added {added} templates, skipped {skipped} existing.")
    print()
    print("Next steps:")
    print("  1. Close OBS completely (if running)")
    print("  2. Reopen OBS")
    print("  3. All templates appear in VinciFlow dock, pre-configured")
    print()
    print("Or if OBS is running with WebSocket enabled:")
    print("  Send ReloadFromDisk via obs-websocket to hot-reload")


if __name__ == "__main__":
    main()
