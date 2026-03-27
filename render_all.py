#!/usr/bin/env python3
"""
render_all.py  —  Convert every .qmd file to HTML in the same directory.
Output sits next to the source .qmd files (no _site/ subfolder).
"""
import sys, os, glob, importlib.util

# Always work relative to where this script lives
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

converter = os.path.join(script_dir, "qmd_to_html.py")
if not os.path.exists(converter):
    print("ERROR: qmd_to_html.py not found next to render_all.py")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("qmd_to_html", converter)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

errors = []

# index.qmd → index.html  (same folder)
if os.path.exists("index.qmd"):
    try:
        mod.qmd_to_html("index.qmd", "index.html")
    except Exception as e:
        errors.append(f"index.qmd: {e}")
else:
    print("  ⚠  index.qmd not found — skipping")

# pages/*.qmd → pages/*.html  (same folder)
qmd_files = sorted(glob.glob("pages/*.qmd"))
if not qmd_files:
    print("  ⚠  No .qmd files found in pages/")

for qmd in qmd_files:
    name = os.path.splitext(qmd)[0]   # e.g. pages/alphabet
    out  = name + ".html"             # e.g. pages/alphabet.html
    try:
        mod.qmd_to_html(qmd, out)
    except Exception as e:
        errors.append(f"{qmd}: {e}")

if errors:
    print(f"\n  ERROR - {len(errors)} file(s) failed:")
    for e in errors:
        print(f"     {e}")
    sys.exit(1)

total = (1 if os.path.exists("index.qmd") else 0) + len(qmd_files)
print(f"\n  {total} file(s) rendered successfully.")
print(f"  Open: {os.path.abspath('index.html')}")
