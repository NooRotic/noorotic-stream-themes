#!/usr/bin/env python3
"""List all VinciFlow lower thirds with their IDs and visibility status."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vinci_ws

items_result = vinci_ws.run("ListLowerThirds")
if not items_result or "items" not in items_result:
    print("Could not list lower thirds")
    sys.exit(1)

items = items_result["items"]
print(f"{'Label':<35} {'ID':<40} {'Visible'}")
print("-" * 85)

for item in items:
    label = item.get("label", item.get("title", "(no label)"))
    lt_id = item.get("id", "?")
    visible = "YES" if item.get("isVisible", False) else ""
    print(f"{label:<35} {lt_id:<40} {visible}")

print(f"\nTotal: {len(items)} lower thirds")
