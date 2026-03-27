#!/usr/bin/env python3
"""
qmd_to_html.py  —  Convert Quarto .qmd files to self-contained HTML
without needing Quarto installed.

Handles:
  - YAML front matter (title, include-in-header)
  - ```{=html} ... ``` raw HTML blocks
  - ::: {.callout-note/tip/warning/important} ... ::: callouts
  - ::: {.dialogue} ... ::: divs
  - ::: {#sec-*} ... ::: section wrappers (transparent)
  - Markdown tables
  - ## / ### headings
  - Horizontal rules ---
  - Bold/italic inline markdown
  - Inline code
  - Embeds shared CSS and JS inline for true self-contained output
"""

import re, sys, os
from pathlib import Path


# ── Callout icons & labels ───────────────────────────────────────────────────
CALLOUT_META = {
    'callout-note':      ('💡', 'Note',      '#dbeafe', '#1e40af'),
    'callout-tip':       ('✅', 'Tip',       '#dcfce7', '#166534'),
    'callout-warning':   ('⚠️', 'Warning',   '#fef9c3', '#854d0e'),
    'callout-important': ('🔴', 'Important', '#fee2e2', '#991b1b'),
}


# ── YAML front-matter parser ──────────────────────────────────────────────────
def parse_front_matter(text):
    """Return (meta_dict, body_text). Only parses what we need."""
    if not text.startswith('---'):
        return {}, text
    end = text.find('\n---', 3)
    if end == -1:
        return {}, text
    yaml_block = text[3:end]
    body = text[end+4:]

    meta = {}
    # title
    m = re.search(r'^title:\s*"(.+?)"', yaml_block, re.MULTILINE)
    if m:
        meta['title'] = m.group(1)

    # include-in-header text block (for <link> tags etc.)
    # We look for the indented block after "text: |"
    header_text = []
    in_header = False
    header_indent = None
    for line in yaml_block.splitlines():
        if re.match(r'\s*text:\s*\|', line):
            in_header = True
            header_indent = None
            continue
        if in_header:
            # Detect indent level from first non-empty line
            if line.strip() == '':
                header_text.append('')
                continue
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if header_indent is None:
                header_indent = indent
            if indent >= header_indent:
                header_text.append(line[header_indent:])
            else:
                # De-dented: end of block
                in_header = False
    meta['include_in_header'] = '\n'.join(header_text)
    return meta, body


# ── Inline markdown ───────────────────────────────────────────────────────────
def render_inline(text):
    """Bold, italic, inline code."""
    # inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


# ── Markdown table → HTML ─────────────────────────────────────────────────────
def render_table(lines):
    rows = []
    for line in lines:
        if re.match(r'\s*\|[-| :]+\|\s*$', line):
            continue   # separator row
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    if not rows:
        return ''
    html = '<div class="table-wrap"><table class="md-table">\n'
    # first row is header
    html += '<thead><tr>' + ''.join(f'<th>{render_inline(c)}</th>' for c in rows[0]) + '</tr></thead>\n'
    if len(rows) > 1:
        html += '<tbody>\n'
        for row in rows[1:]:
            html += '<tr>' + ''.join(f'<td>{render_inline(c)}</td>' for c in row) + '</tr>\n'
        html += '</tbody>\n'
    html += '</table></div>\n'
    return html


# ── Callout block → HTML ─────────────────────────────────────────────────────
def render_callout(cls, inner_html):
    icon, label, bg, color = CALLOUT_META.get(cls, ('ℹ️', 'Note', '#f0f4ff', '#1e3a8a'))
    return (
        f'<div class="callout callout-{cls.split("-",1)[1]}" '
        f'style="background:{bg};border-left:4px solid {color};'
        f'border-radius:10px;padding:1rem 1.2rem;margin:1.2rem 0;">\n'
        f'<div style="font-weight:800;color:{color};margin-bottom:.4rem;">'
        f'{icon} {label}</div>\n'
        f'<div style="color:#1a1a2e;">{inner_html}</div>\n'
        f'</div>\n'
    )


# ── Block-level parser ────────────────────────────────────────────────────────
def render_blocks(body):
    """
    Parse the body (after front matter) into HTML.
    Handles raw HTML blocks, ::: fenced divs, tables, headings, hr, paragraphs.
    """
    lines = body.splitlines()
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ── Raw HTML block ````{=html} ... ` `` ──────────────────────────────
        if re.match(r'```\{=html\}', line):
            i += 1
            raw = []
            while i < len(lines) and not lines[i].startswith('```'):
                raw.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            out.append('\n'.join(raw))
            continue

        # ── Fenced div ::: ───────────────────────────────────────────────────
        m = re.match(r'^:::(.*)$', line)
        if m:
            attrs = m.group(1).strip()
            # Closing :::
            if not attrs:
                # This is a closing ::: — handled inside the opener below.
                # If we encounter an unexpected closer, just skip.
                i += 1
                continue

            # Opener — collect inner lines until matching closer
            depth = 1
            i += 1
            inner_lines = []
            while i < len(lines):
                if re.match(r'^:::\s*$', lines[i]):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                    inner_lines.append(lines[i])
                elif re.match(r'^:::', lines[i]):
                    depth += 1
                    inner_lines.append(lines[i])
                else:
                    inner_lines.append(lines[i])
                i += 1

            inner_html = render_blocks('\n'.join(inner_lines))

            # Decide how to wrap
            cls_m = re.search(r'\{\.([^}]+)\}', attrs)
            id_m  = re.search(r'\{#([^}]+)\}', attrs)

            if cls_m:
                cls = cls_m.group(1).strip()
                if cls in CALLOUT_META:
                    out.append(render_callout(cls, inner_html))
                elif cls == 'dialogue':
                    out.append(
                        f'<div class="dialogue" style="background:#f5f3ff;'
                        f'border-radius:12px;padding:1rem 1.4rem;margin:1.2rem 0;">'
                        f'{inner_html}</div>\n'
                    )
                else:
                    out.append(f'<div class="{cls}">{inner_html}</div>\n')
            elif id_m:
                sec_id = id_m.group(1).strip()
                out.append(f'<section id="{sec_id}">{inner_html}</section>\n')
            else:
                out.append(inner_html)
            continue

        # ── Markdown table ────────────────────────────────────────────────────
        if re.match(r'\s*\|', line):
            tbl_lines = []
            while i < len(lines) and re.match(r'\s*\|', lines[i]):
                tbl_lines.append(lines[i])
                i += 1
            out.append(render_table(tbl_lines))
            continue

        # ── ATX headings ##, ### ──────────────────────────────────────────────
        m = re.match(r'^(#{1,6})\s+(.+?)(?:\s+\{#[\w-]+\})?\s*$', line)
        if m:
            level = len(m.group(1))
            text  = render_inline(m.group(2))
            # Extract optional ID
            id_attr = ''
            id_m2 = re.search(r'\{#([\w-]+)\}', line)
            if id_m2:
                id_attr = f' id="{id_m2.group(1)}"'
                text = render_inline(re.sub(r'\s*\{#[\w-]+\}', '', m.group(2)))
            out.append(f'<h{level}{id_attr} style="margin:1.4rem 0 .6rem;color:#2d2250;">'
                       f'{text}</h{level}>\n')
            i += 1
            continue

        # ── Horizontal rule ---  ─────────────────────────────────────────────
        if re.match(r'^---+\s*$', line):
            out.append('<hr style="border:none;border-top:2px solid #e9d5ff;margin:2rem 0;">\n')
            i += 1
            continue

        # ── HTML comment (pass through) ───────────────────────────────────────
        if line.strip().startswith('<!--'):
            out.append(line + '\n')
            i += 1
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if line.strip() == '':
            i += 1
            continue

        # ── Paragraph: collect consecutive non-special lines ──────────────────
        para_lines = []
        while i < len(lines):
            l = lines[i]
            if (l.strip() == '' or
                re.match(r'```', l) or
                re.match(r'^:::', l) or
                re.match(r'^#{1,6}\s', l) or
                re.match(r'^---+\s*$', l) or
                re.match(r'\s*\|', l)):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            # Handle line breaks (two trailing spaces or explicit <br>)
            joined = ' '.join(para_lines)
            # Quarto line-break: trailing two spaces or backslash
            joined = re.sub(r'  \n?', '<br>', joined)
            joined = re.sub(r'\\\n', '<br>', joined)
            out.append(f'<p style="margin:.5rem 0 .8rem;line-height:1.7;">'
                       f'{render_inline(joined)}</p>\n')

    return ''.join(out)


# ── CSS/JS embedding ──────────────────────────────────────────────────────────
MD_TABLE_CSS = """
<style>
.table-wrap { overflow-x: auto; margin: 1.2rem 0; }
.md-table { border-collapse: collapse; width: 100%; font-size: .9rem; }
.md-table th { background: #7c3aed; color: #fff; padding: .55rem .9rem; text-align: left; }
.md-table td { padding: .45rem .9rem; border-bottom: 1px solid #e9d5ff; }
.md-table tr:nth-child(even) td { background: #f5f0ff; }
</style>
"""


def read_file(path):
    return Path(path).read_text(encoding='utf-8')


def embed_asset(tag_html, base_dir):
    """
    Given an HTML tag referencing a relative file, return
    an equivalent inline <style> or <script> tag.
    """
    # <link rel="stylesheet" href="...">
    m = re.search(r'href=["\']([^"\']+\.css)["\']', tag_html)
    if m:
        rel = m.group(1)
        full = (Path(base_dir) / rel).resolve()
        if full.exists():
            css = full.read_text(encoding='utf-8')
            return f'<style>{css}</style>'
        return tag_html  # keep as-is if file not found

    # <script src="...">
    m = re.search(r'src=["\']([^"\']+\.js)["\']', tag_html)
    if m:
        rel = m.group(1)
        full = (Path(base_dir) / rel).resolve()
        if full.exists():
            js = full.read_text(encoding='utf-8')
            return f'<script>{js}</script>'
        return tag_html

    return tag_html


def inline_assets(html, base_dir):
    """
    Replace <link href="...css"> and <script src="...js"> with inline equivalents.
    Google Fonts links are left as external (they need network).
    """
    def replace_link(m):
        tag = m.group(0)
        if 'fonts.googleapis.com' in tag:
            return tag
        return embed_asset(tag, base_dir)

    def replace_script(m):
        tag = m.group(0)
        return embed_asset(tag, base_dir)

    html = re.sub(r'<link[^>]+/?>', replace_link, html)
    html = re.sub(r'<script src=["\'][^"\']+["\'][^>]*></script>', replace_script, html)
    return html


# ── Full document assembly ────────────────────────────────────────────────────
def qmd_to_html(qmd_path, out_path):
    src  = Path(qmd_path)
    base = src.parent          # directory containing the .qmd

    text = src.read_text(encoding='utf-8')
    meta, body = parse_front_matter(text)

    title           = meta.get('title', 'German A1')
    include_header  = meta.get('include_in_header', '')

    # Inline local assets referenced in include_in_header
    include_header = inline_assets(include_header, base)

    # Convert body to HTML
    content_html = render_blocks(body)

    # Inline any remaining local asset tags in content
    content_html = inline_assets(content_html, base)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{include_header}
{MD_TABLE_CSS}
</head>
<body>
{content_html}
</body>
</html>
"""

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(full_html, encoding='utf-8')
    print(f'  ✓ {Path(out_path).name}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 qmd_to_html.py input.qmd output.html')
        sys.exit(1)
    qmd_to_html(sys.argv[1], sys.argv[2])
