#!/usr/bin/env python3
"""Show a VinciFlow lower third by label or ID.

Usage:
  python3 vinci-show.py "LT: Scoreboard"
  python3 vinci-show.py lt_abc123
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vinci_ws

if len(sys.argv) < 2:
    print("Usage: vinci-show.py <label-or-id>")
    sys.exit(1)

target = sys.argv[1]

items_result = vinci_ws.run("ListLowerThirds")
if not items_result or "items" not in items_result:
    print("Could not list lower thirds")
    sys.exit(1)

match = None
for item in items_result["items"]:
    if item.get("id") == target or item.get("label", "").lower() == target.lower() or item.get("title", "").lower() == target.lower():
        match = item
        break

if not match:
    print(f"Lower third not found: {target}")
    sys.exit(1)

lt_id = match["id"]
name = match.get("label", match.get("title", lt_id))

vinci_ws.run("SetVisible", {"id": lt_id, "visible": True})
print(f"Shown: {name} ({lt_id})")
