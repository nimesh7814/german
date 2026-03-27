#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  build.sh  —  Render the entire German A1 site with one command
#
#  Usage:
#    ./build.sh          → render all pages to _site/
#    ./build.sh --serve  → render + live-reload preview
#
#  Adding a new topic:
#    1. Drop a new pages/mytopic.qmd file (copy any existing page as template)
#    2. Add a card for it in index.qmd
#    3. Run ./build.sh  — the nav bar in ALL pages auto-updates
# ─────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   🇩🇪  German A1 — Building HTML site        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Auto-regenerate nav bars in all pages/*.qmd ──────────
echo "▶  Syncing nav bars across all pages..."
python3 - << 'PYEOF'
import os, re, glob

pages_dir = "pages"
qmd_files = sorted(glob.glob(os.path.join(pages_dir, "*.qmd")))

# Build ordered tab list from filenames + titles in each file
tabs = []
for path in qmd_files:
    key = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Extract title from YAML front matter
    m = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
    title = m.group(1) if m else key.title()
    tabs.append((key, title, path))

# Rebuild the nav-tabs block inside each file
NAV_COMMENT = "<!-- AUTO-NAV-START -->"
NAV_END     = "<!-- AUTO-NAV-END -->"

for current_key, _, current_path in tabs:
    tab_lines = ""
    for key, title, _ in tabs:
        active = ' class="nav-tab active"' if key == current_key else ' class="nav-tab"'
        tab_lines += f'    <a{active} href="{key}.html">{title}</a>\n'

    new_nav = (
        f'{NAV_COMMENT}\n'
        f'<div id="nav-tabs">\n'
        f'{tab_lines}'
        f'</div>\n'
        f'{NAV_END}'
    )

    with open(current_path, encoding="utf-8") as f:
        content = f.read()

    # Replace existing AUTO-NAV block if present
    if NAV_COMMENT in content and NAV_END in content:
        content = re.sub(
            re.escape(NAV_COMMENT) + r'.*?' + re.escape(NAV_END),
            new_nav,
            content,
            flags=re.DOTALL
        )
        with open(current_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ nav updated: {os.path.basename(current_path)}")
    else:
        print(f"  ⚠  no AUTO-NAV markers in {os.path.basename(current_path)} — skipping nav update")

print(f"\n  {len(tabs)} page(s) processed.")
PYEOF

echo ""

# ── Step 2: Render ────────────────────────────────────────────────
if [[ "$1" == "--serve" ]]; then
  echo "▶  quarto preview (live reload)..."
  quarto preview .
else
  echo "▶  quarto render..."
  quarto render .
  echo ""
  echo "✅  Done!  Output in:  _site/"
  echo ""
  echo "   Open:  _site/index.html"
  echo ""
fi
