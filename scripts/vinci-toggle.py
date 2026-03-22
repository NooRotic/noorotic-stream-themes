#!/usr/bin/env python3
"""Toggle a VinciFlow lower third by label or ID.

Usage:
  python3 vinci-toggle.py "LT: Neon Pulse"
  python3 vinci-toggle.py lt_abc123
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vinci_ws

if len(sys.argv) < 2:
    print("Usage: vinci-toggle.py <label-or-id>")
    sys.exit(1)

target = sys.argv[1]

# List all lower thirds to find the target
items_result = vinci_ws.run("ListLowerThirds")
if not items_result or "items" not in items_result:
    print("Could not list lower thirds")
    sys.exit(1)

items = items_result["items"]

# Match by label or ID
match = None
for item in items:
    if item.get("id") == target or item.get("label", "").lower() == target.lower() or item.get("title", "").lower() == target.lower():
        match = item
        break

if not match:
    print(f"Lower third not found: {target}")
    print(f"Available: {', '.join(i.get('label', i.get('title', i['id'])) for i in items)}")
    sys.exit(1)

lt_id = match["id"]
name = match.get("label", match.get("title", lt_id))

result = vinci_ws.run("ToggleVisible", {"id": lt_id})
print(f"Toggled: {name} ({lt_id})")
