#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  build.sh  —  Render the entire German A1 site with one command
#
#  Usage:
#    ./build.sh          → render all pages to _site/
#    ./build.sh --serve  → render + live-preview (Python http.server)
#
#  Requirements:
#    Python 3  (no Quarto needed — uses qmd_to_html.py)
#
#  Adding a new topic:
#    1. Drop a new pages/mytopic.qmd file (copy any existing page)
#    2. Add a card for it in index.qmd
#    3. Run ./build.sh  — the nav bar in ALL pages auto-updates
# ─────────────────────────────────────────────────────────────────
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   🇩🇪  German A1 — Building HTML site        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Auto-regenerate nav bars in all pages/*.qmd ──────────
echo "▶  Syncing nav bars across all pages..."
python3 "$SCRIPT_DIR/nav_sync.py"
echo ""

# ── Step 2: Convert QMD → self-contained HTML ─────────────────────
echo "▶  Converting .qmd files to HTML..."
mkdir -p _site/pages
python3 "$SCRIPT_DIR/render_all.py"
echo ""

echo "✅  Done!  Output in:  _site/"
echo ""
echo "   Open:  _site/index.html"
echo ""

# ── Step 3 (optional): --serve ─────────────────────────────────────
if [[ "$1" == "--serve" ]]; then
  echo "▶  Serving at http://localhost:8000  (Ctrl-C to stop)"
  cd _site
  python3 -m http.server 8000
fi
