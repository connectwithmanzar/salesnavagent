#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/make_icons.py"
STAGE="$(mktemp -d)"
DEST="$STAGE/salesnav-list-save"
mkdir -p "$DEST"
cp "$ROOT/extension/manifest.json" "$DEST/"
cp "$ROOT/extension/"*.js "$DEST/"
cp "$ROOT/extension/"*.html "$DEST/" 2>/dev/null || true
cp "$ROOT/extension/"*.css "$DEST/" 2>/dev/null || true
mkdir -p "$DEST/icons"
cp "$ROOT/extension/icons/"*.png "$DEST/icons/"
mkdir -p "$ROOT/docs"
rm -f "$ROOT/docs/salesnav-list-save.zip"
(cd "$STAGE" && zip -r "$ROOT/docs/salesnav-list-save.zip" salesnav-list-save)
rm -rf "$STAGE"
echo "wrote $ROOT/docs/salesnav-list-save.zip"
