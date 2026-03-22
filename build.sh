#!/usr/bin/env bash
# Build VinciFlow-importable ZIP packages from template sources.
# Usage: ./build.sh [theme-name]   (omit theme-name to build all)

set -euo pipefail

SRC_DIR="template_sources"
OUT_DIR="template_packages"

if [ ! -d "$SRC_DIR" ]; then
  echo "Error: $SRC_DIR directory not found. Run from repo root."
  exit 1
fi

mkdir -p "$OUT_DIR"

build_theme() {
  local name="$1"
  local src="$SRC_DIR/$name"

  if [ ! -f "$src/template.html" ] || [ ! -f "$src/template.css" ] || [ ! -f "$src/template.json" ]; then
    echo "  SKIP  $name (missing required files)"
    return
  fi

  local zip="$OUT_DIR/$name.zip"

  python3 -c "
import zipfile, os, sys
src, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in os.listdir(src):
        path = os.path.join(src, f)
        if os.path.isfile(path):
            zf.write(path, f)
" "$src" "$zip"

  local size
  size=$(du -h "$zip" | cut -f1)
  echo "  BUILD $name.zip ($size)"
}

if [ $# -gt 0 ]; then
  for name in "$@"; do
    if [ -d "$SRC_DIR/$name" ]; then
      build_theme "$name"
    else
      echo "  ERROR $name not found in $SRC_DIR/"
    fi
  done
else
  echo "Building all VinciFlow theme packages..."
  echo ""
  for dir in "$SRC_DIR"/*/; do
    name="$(basename "$dir")"
    build_theme "$name"
  done
fi

echo ""
echo "Done. Packages in $OUT_DIR/"
