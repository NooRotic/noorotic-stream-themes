#!/usr/bin/env python3
"""Hide all visible VinciFlow lower thirds."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vinci_ws

result = vinci_ws.run("GetVisible")
if not result:
    print("No response from VinciFlow")
    sys.exit(1)

visible = result.get("visibleIds", result.get("ids", []))
if not visible:
    print("No lower thirds currently visible")
    sys.exit(0)

print(f"Hiding {len(visible)} lower third(s)...")
for item in visible:
    # Handle both string IDs and object format
    lt_id = item.get("id") if isinstance(item, dict) else item
    vinci_ws.run("SetVisible", {"id": lt_id, "visible": False})
    print(f"  Hidden: {lt_id}")

print("Done — all lower thirds hidden")
