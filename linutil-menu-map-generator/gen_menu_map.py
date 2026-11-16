#!/usr/bin/env python3
"""Generate the Linutil menu map (HTML/SVG) from core/tabs/*/tab_data.toml."""
import html
import math
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABS = ROOT / 'linutil' / 'core' / 'tabs'
OUT = ROOT / 'linutil-menu-map'

# Colors are CSS variables; the light and dark values live in THEME below.
C = {k: f'var(--color-{k.replace("_", "-")})' for k in (
    'paper', 'zone', 'node', 'leaf', 'ink', 'muted', 'soft', 'accent',
    'tint', 'rule', 'rail', 'chip_ink', 'chip_accent')}

LIGHT_VARS = """
  --color-paper: #e6e5e0; --color-zone: #dddcd6; --color-paper-2: #dddcd6;
  --color-node: #efeeea; --color-leaf: #e9e8e3;
  --color-ink: #2d3142; --color-muted: #4f5d75; --color-soft: #566178; --color-accent: #a83a18;
  --color-tint: rgba(168,58,24,0.10); --color-rule: rgba(45,49,66,0.16); --color-rail: rgba(45,49,66,0.40);
  --color-chip-ink: rgba(45,49,66,0.40); --color-chip-accent: rgba(168,58,24,0.50);
"""
# archboki_nvim palette: background #1d283a, foreground #c9e79a, gray #94a3b8,
# darkblue #141c2a, cursorline #28334a, orange #F78C6C.
DARK_VARS = """
  --color-paper: #1d283a; --color-zone: #141c2a; --color-paper-2: #141c2a;
  --color-node: #28334a; --color-leaf: #222d42;
  --color-ink: #c9e79a; --color-muted: #94a3b8; --color-soft: #94a3b8; --color-accent: #F78C6C;
  --color-tint: rgba(247,140,108,0.14); --color-rule: rgba(148,163,184,0.22); --color-rail: rgba(148,163,184,0.50);
  --color-chip-ink: rgba(201,231,154,0.40); --color-chip-accent: rgba(247,140,108,0.55);
"""
THEME = f"""
:root {{{LIGHT_VARS}
  --font-sans: 'Geist', system-ui, sans-serif;
  --font-serif: 'Instrument Serif', serif;
  --font-mono: 'Geist Mono', ui-monospace, monospace;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{{DARK_VARS}  color-scheme: dark; }}
}}
:root[data-theme="dark"] {{{DARK_VARS}  color-scheme: dark; }}
:root[data-theme="light"] {{ color-scheme: light; }}
"""
SANS = "'Geist', sans-serif"
MONO = "'Geist Mono', monospace"
GROUP_LIMIT = 6  # more direct actions than this -> one grouped node


def g4(v):
    return int(math.ceil(v / 4)) * 4


def esc(s):
    return html.escape(s, quote=True)


def tw(s, size, factor):
    return len(s) * size * factor


# ---------------------------------------------------------------- data
def leaves(es):
    return sum(leaves(e['entries']) if 'entries' in e else 1 for e in es)


def load():
    order = tomllib.load(open(TABS / 'tabs.toml', 'rb'))['directories']
    tabs = []
    for d in order:
        t = tomllib.load(open(TABS / d / 'tab_data.toml', 'rb'))
        folders, loose = [], []
        for e in t['data']:
            if 'entries' in e:
                subs = [(c['name'], leaves(c['entries']))
                        for c in e['entries'] if 'entries' in c]
                folders.append(dict(name=e['name'], leaves=leaves(e['entries']), subs=subs))
            else:
                loose.append(e['name'])
        tabs.append(dict(dir=d, name=t['name'], folders=folders, loose=loose,
                         total=leaves(t['data']), raw=t['data']))
    return tabs


def folder_sub(f):
    s = f"{f['leaves']} actions"
    if f['subs']:
        s += f" · {len(f['subs'])} submenus"
    return s


# ------------------------------------------------------------ primitives
def text(x, y, s, size, fill, family, weight=None, anchor='middle', extra=''):
    w = f' font-weight="{weight}"' if weight else ''
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}"{w} '
            f'font-family="{family}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def node(x, y, w, h, name, sub=None, kind='menu', tag=None):
    out = []
    if kind == 'root':
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{C["paper"]}"/>')
        fill, stroke, sw, dash = C['tint'], C['accent'], 1, ''
        chip = C['chip_accent']; tagfill = C['accent']
    elif kind in ('tab', 'menu'):
        fill, stroke, sw, dash = C['node'], C['ink'], 1, ''
        chip = C['chip_ink']; tagfill = C['ink']
    elif kind == 'leaf':
        fill, stroke, sw, dash = C['leaf'], C['muted'], 0.8, ''
        chip = tagfill = None
    else:  # group
        fill, stroke, sw, dash = C['leaf'], C['muted'], 1, ' stroke-dasharray="4,3"'
        chip = tagfill = None
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="{sw}"{dash}/>')
    cx = x + w // 2
    if tag:
        cw = g4(len(tag) * 5.2 + 12)
        out.append(f'<rect x="{x + 8}" y="{y + 8}" width="{cw}" height="12" rx="2" '
                   f'fill="transparent" stroke="{chip}" stroke-width="0.8"/>')
        out.append(text(x + 8 + cw // 2, y + 17, tag, 7, tagfill, MONO,
                        extra=' letter-spacing="0.08em"'))
    if sub:
        out.append(text(cx, y + h - 16, name, 12, C['ink'], SANS, 600))
        out.append(text(cx, y + h - 4, sub, 9, C['soft'], MONO))
    else:
        out.append(text(cx, y + h // 2 + 4, name, 12, C['ink'], SANS, 600))
    return '\n'.join(out)


def zone(x, y, w, h, label):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{C["zone"]}" '
            f'stroke="{C["rule"]}" stroke-width="1"/>\n'
            + text(x + 16, y + 20, label, 8, C['muted'], MONO, anchor='start',
                   extra=' letter-spacing="0.18em"'))


def path(d, color=None, w=1):
    return (f'<path d="{d}" fill="none" stroke="{color or C["muted"]}" '
            f'stroke-width="{w}"/>')


def legend(y0, items, note=None, width=None):
    """items: list of (kind, label). Returns svg and final x."""
    out = [f'<line x1="40" y1="{y0}" x2="{(width or 960) - 40}" y2="{y0}" '
           f'stroke="{C["rule"]}" stroke-width="0.8"/>',
           text(40, y0 + 16, 'LEGEND', 8, C['muted'], MONO, anchor='start',
                extra=' letter-spacing="0.18em"')]
    x = 40
    ky = y0 + 28
    for kind, label in items:
        if kind == 'root':
            r = f'fill="{C["tint"]}" stroke="{C["accent"]}" stroke-width="1"'
        elif kind in ('tab', 'menu'):
            r = f'fill="{C["node"]}" stroke="{C["ink"]}" stroke-width="1"'
        elif kind == 'leaf':
            r = f'fill="{C["leaf"]}" stroke="{C["muted"]}" stroke-width="0.8"'
        else:
            r = (f'fill="{C["leaf"]}" stroke="{C["muted"]}" stroke-width="1" '
                 f'stroke-dasharray="4,3"')
        out.append(f'<rect x="{x}" y="{ky}" width="14" height="10" rx="2" {r}/>')
        out.append(text(x + 20, ky + 8, label, 8.5, C['muted'], SANS, anchor='start'))
        x += 20 + int(len(label) * 5.2) + 28
    if note:
        out.append(text(x + 8, ky + 8, note, 8.5, C['muted'], SANS, anchor='start',
                        extra=' font-style="italic"'))
    return '\n'.join(out)


def svg_wrap(slug, title, desc, W, H, body):
    floor = g4(max(520, W * 0.85))
    style = f'width:100%;max-width:{W}px;min-width:{floor}px;height:auto'
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc" style="{style}">\n'
            f'<title id="{slug}-title">{esc(title)}</title>\n'
            f'<desc id="{slug}-desc">{esc(desc)}</desc>\n'
            f'<rect width="100%" height="100%" fill="{C["paper"]}"/>\n'
            f'{body}\n</svg>')


# -------------------------------------------------------------- overview
ICON_PATHS = {
    'menu': '<rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 6.5h6M5 9.5h6M5 12.5h3.5"/>',
    'folder': '<path d="M1.6 5.2h4.4l1.5 1.6h7v6.8h-12.9z"/>',
    'script': '<rect x="2" y="2.5" width="12" height="11" rx="2"/><path d="M5 7.1 7.3 9.2 5 11.3M8.7 11.3h2.8"/>',
}


def icon_svg(mark, x, y, color=None):
    color = color or C['ink']
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" '
            f'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICON_PATHS[mark]}</g>')


def html_icon(mark):
    return (f'<svg class="glyph" viewBox="0 0 16 16" aria-hidden="true" fill="none" '
            f'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICON_PATHS[mark]}</svg>')


def norm_rail(item):
    if len(item) == 2:
        return item[0], item[1], 0
    return item


def draw_rail(body, railx, top, rail):
    step = 26
    if not rail:
        return top
    first = top + 22
    last = first + (len(rail) - 1) * step
    body.append(f'<line x1="{railx}" y1="{top}" x2="{railx}" y2="{last}" '
                f'stroke="{C["rail"]}" stroke-width="0.8"/>')
    for j, item in enumerate(rail):
        label, rmark, indent = norm_rail(item)
        cy = first + j * step
        ix = railx + 14 + indent * 14
        body.append(f'<line x1="{railx}" y1="{cy}" x2="{ix - 2}" y2="{cy}" '
                    f'stroke="{C["rail"]}" stroke-width="0.8"/>')
        body.append(icon_svg(rmark, ix, cy - 11))
        body.append(text(ix + 18, cy + 3, label, 11, C['ink'], SANS, anchor='start'))
    return last


def legend_marks(y0, note, width):
    items = [('menu', 'Menu'), ('folder', 'Submenu'), ('script', 'Action')]
    out = [f'<line x1="40" y1="{y0}" x2="{width - 40}" y2="{y0}" stroke="{C["rule"]}" stroke-width="0.8"/>',
           text(40, y0 + 16, 'LEGEND', 8, C['muted'], MONO, anchor='start',
                extra=' letter-spacing="0.18em"')]
    x, ky = 40, y0 + 28
    for mark, label in items:
        out.append(icon_svg(mark, x, ky - 3))
        out.append(text(x + 22, ky + 9, label, 8.5, C['muted'], SANS, anchor='start'))
        x += 22 + int(len(label) * 5.2) + 26
    extra = 0
    if note:
        note_w = int(len(note) * 4.8)
        if x + 8 + note_w <= width - 40:
            out.append(text(x + 8, ky + 9, note, 8.5, C['muted'], SANS, anchor='start',
                            extra=' font-style="italic"'))
        else:
            out.append(text(40, ky + 28, note, 8.5, C['muted'], SANS, anchor='start',
                            extra=' font-style="italic"'))
            extra = 22
    return '\n'.join(out), extra


def col_width(columns):
    need = 248
    for name, sub, _kind, _mark, rail in columns:
        need = max(need, int(len(name) * 7.4) + 48, int(len(sub or '') * 6.2) + 48)
        for item in rail or []:
            label, _rmark, indent = norm_rail(item)
            need = max(need, 16 + 14 + indent * 14 + 18 + int(len(label) * 6.6) + 20)
    return g4(min(need, 520))


def split_near_half(items):
    if len(items) <= 4:
        return [items]
    left = (len(items) + 1) // 2
    return split_near_half(items[:left]) + split_near_half(items[left:])


def _columns_svg(slug, title, desc, root_name, root_sub, columns, note):
    n = len(columns)
    tw, gap = col_width(columns), 20
    x0 = 40
    row_w = n * tw + (n - 1) * gap
    width = g4(row_w + 80)
    root_w = min(max(248, int(len(root_name) * 7.4) + 48), row_w)
    root_x = x0 + max(0, (row_w - root_w) // 2)
    root_y, tab_y, h = 40, 156, 72
    centers = [x0 + tw // 2 + i * (tw + gap) for i in range(n)]
    body = [path(f'M {root_x + root_w // 2} {root_y + h} V {root_y + h + 28}')]
    if n > 1:
        body.append(path(f'M {centers[0]} {root_y + h + 28} H {centers[-1]}'))
        for cx in centers:
            body.append(path(f'M {cx} {root_y + h + 28} V {tab_y}'))
    else:
        body.append(path(f'M {root_x + root_w // 2} {root_y + h + 28} V {tab_y}'))
    body.append(node(root_x, root_y, root_w, h, root_name, root_sub, 'root', None))
    # glyph on the root, drawn over the empty tag area
    body.append(icon_svg('menu', root_x + 8, root_y + 8, C['accent']))
    bottom = tab_y + h
    for i, (name, sub, kind, mark, rail) in enumerate(columns):
        tx = x0 + i * (tw + gap)
        body.append(node(tx, tab_y, tw, h, name, sub, kind, None))
        body.append(icon_svg(mark, tx + 8, tab_y + 8))
        if not rail:
            continue
        last = draw_rail(body, tx + 16, tab_y + h, rail)
        bottom = max(bottom, last + 16)
    ly = bottom + 28
    legend, extra = legend_marks(ly, note, width)
    body.append(legend)
    return svg_wrap(slug, title, desc, width, ly + 56 + extra, '\n'.join(body))


def columns_svg(slug, title, desc, root_name, root_sub, columns, note):
    parts = split_near_half(columns)
    if len(parts) == 1:
        return _columns_svg(slug, title, desc, root_name, root_sub, columns, note)
    drawn = []
    for i, part in enumerate(parts):
        slug_i = slug if i == 0 else f'{slug}-{i + 1}'
        title_i = f'{title} · {i + 1} of {len(parts)}'
        drawn.append(_columns_svg(slug_i, title_i, desc, root_name, root_sub, part, note))
    return '\n'.join(drawn)


def rail_from_entries(entries, depth=0):
    rail = []
    for e in entries:
        if 'entries' in e:
            rail.append((e['name'], 'folder', depth))
            rail.extend(rail_from_entries(e['entries'], depth + 1))
        else:
            rail.append((e['name'], 'script', depth))
    return rail


def tab_columns(raw):
    direct, branches = [], []
    for e in raw:
        if 'entries' not in e:
            direct.append((e['name'], 'script'))
            continue
        kids = e['entries']
        nested = any('entries' in c for c in kids)
        if nested or len(kids) > 1:
            branches.append((e['name'], rail_from_entries(kids)))
        elif kids:
            only = kids[0]
            direct.append((only['name'] if 'entries' not in only else e['name'], 'script'))
        else:
            direct.append((e['name'], 'script'))
    columns = []
    if direct:
        n = len(direct)
        sub = f'{n} action' if n == 1 else f'{n} actions'
        columns.append(('Direct actions', sub, 'menu', 'folder', direct))
    for name, rail in branches:
        n = sum(1 for item in rail if norm_rail(item)[1] == 'script')
        sub = f'{n} action' if n == 1 else f'{n} actions'
        columns.append((name, sub, 'menu', 'folder', rail))
    return columns


def overview_columns(tabs):
    columns = []
    for t in tabs:
        rail = []
        for f in t['folders']:
            rail.append((f['name'], 'folder', 0))
            for subname, _cnt in f['subs']:
                rail.append((subname, 'folder', 1))
        if t['loose']:
            n = len(t['loose'])
            rail.append((f'Direct actions · {n}', 'script', 0))
        sub = f"{t['total']} entries"
        columns.append((t['name'], sub, 'menu', 'folder', rail))
    return columns


def overview(tabs):
    total = sum(t['total'] for t in tabs)
    columns = overview_columns(tabs)
    title = 'Linutil menu overview'
    desc = (f'Tree of the Linutil menu: a root with {len(tabs)} top-level tabs, '
            f'{total} entries. A folder is a submenu. Direct actions sit on the tab.')
    svg = columns_svg(
        'linutil-overview', title, desc,
        'Linutil', f'{total} entries · {len(tabs)} tabs', columns,
        'More than four blocks is split near half. Open a tab for every action.')
    return 'linutil-overview', svg, 0, title, desc


def tab_diagram(t):
    slug = f"linutil-{t['dir']}"
    columns = tab_columns(t['raw'])
    # A tab that is only direct actions is one trunk, not a block named Direct actions under itself.
    only_direct = len(columns) == 1 and columns[0][0] == 'Direct actions'
    title = f"Linutil menu: {t['name']}"
    n_menus = len(t['folders'])
    parts = []
    if n_menus:
        parts.append(f"{n_menus} submenus")
    if t['loose']:
        parts.append(f"{len(t['loose'])} direct actions")
    desc = (f"Tree of the {t['name']} tab in Linutil, {t['total']} entries across "
            f"{' and '.join(parts)}.")
    note = 'A folder opens another menu. A shell mark is one action. Blocks past four are split near half.'
    if only_direct:
        rail = columns[0][4]
        tw = col_width([(t['name'], columns[0][1], 'menu', 'menu', rail)])
        width = g4(max(tw + 80, 560))
        x0, h = 40, 72
        root_w = min(tw, max(248, int(len(t['name']) * 7.4) + 48))
        root_x = x0 + max(0, (tw - root_w) // 2)
        body = [node(root_x, 40, root_w, h, t['name'], columns[0][1], 'root', None),
                icon_svg('menu', root_x + 8, 48, C['accent'])]
        last = draw_rail(body, x0 + 16, 40 + h, rail)
        ly = last + 28
        legend, extra = legend_marks(ly, note, width)
        body.append(legend)
        svg = svg_wrap(slug, title, desc, width, ly + 56 + extra, '\n'.join(body))
    else:
        svg = columns_svg(slug, title, desc, t['name'], f"{t['total']} entries", columns, note)
    return slug, svg, 0, title, desc



# ------------------------------------------------------------------ pages
CSS_BASE = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
/*THEME*/
body { font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink);
  min-height: 100vh; padding: 3rem 2rem; }
.frame { max-width: 1440px; width: 100%; margin: 0 auto; }
.eyebrow { font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }
h1 { font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem);
  font-weight: 400; letter-spacing: -0.02em; line-height: 1.15; color: var(--color-ink);
  margin-bottom: 0.5rem; }
.lede { font-size: 0.9rem; color: var(--color-muted); margin-bottom: 1.5rem; max-width: 64ch; }
.diagram-container { width: 100%; overflow-x: auto; display: flex; flex-direction: column; gap: 1.75rem; }
svg { width: 100%; display: block; height: auto; }
.glyph { width: 0.95rem; height: 0.95rem; flex: none; color: var(--color-ink); }
.nm { display: flex; align-items: center; gap: 0.4rem; }
.subtab { display: inline-flex; align-items: center; gap: 0.35rem; }
h3.sub { display: flex; align-items: center; gap: 0.35rem; }
h3.sub .glyph { width: 0.8rem; height: 0.8rem; }
@media print { .diagram-container { overflow-x: visible; } svg { min-width: 0 !important; } }
"""
CSS_BASE = CSS_BASE.replace('/*THEME*/', THEME)

CSS_TABS = """
.tabs { display: flex; flex-wrap: wrap; gap: 0.25rem; border-bottom: 1px solid var(--color-rule);
  margin-bottom: 1.5rem; }
.tab { font: 500 0.82rem var(--font-sans); color: var(--color-muted); background: none;
  border: 0; border-bottom: 2px solid transparent; padding: 0.6rem 0.9rem; cursor: pointer;
  margin-bottom: -1px; }
.tab .n { font-family: var(--font-mono); font-size: 0.68rem; color: var(--color-soft); margin-left: 0.4rem; }
.tab:hover { color: var(--color-ink); }
.tab[aria-selected="true"] { color: var(--color-ink); border-bottom-color: var(--color-ink); }
.tab:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
.js .panel[hidden] { display: none; }
.panel + .panel { margin-top: 3rem; }
.js .panel + .panel { margin-top: 0; }
"""

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
         '&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" '
         'rel="stylesheet">')


def lede_for(t):
    parts = []
    if t['folders']:
        acts = sum(f['leaves'] for f in t['folders'])
        parts.append(f"{len(t['folders'])} submenus ({acts} actions)")
    if t['loose']:
        parts.append(f"{len(t['loose'])} direct actions")
    return f"{t['total']} entries: " + ' and '.join(parts) + '.'


def standalone(slug, title, h1, lede, svg):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  {FONTS}
  <style>{CSS_BASE}</style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Menu map · Tree</p>
    <h1>{esc(h1)}</h1>
    <p class="lede">{esc(lede)}</p>
    <div class="diagram-container">
{svg}
    </div>
  </div>
</body>
</html>
"""


def wrapper(panels, tabs):
    buttons, secs = [], []
    for i, (slug, label, count, lede, svg) in enumerate(panels):
        sel = 'true' if i == 0 else 'false'
        n = f'<span class="n">{count}</span>' if count else ''
        buttons.append(f'<button class="tab" role="tab" id="tab-{slug}" aria-controls="panel-{slug}" '
                       f'aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{esc(label)}{n}</button>')
        secs.append(f'<section class="panel" role="tabpanel" id="panel-{slug}" '
                    f'aria-labelledby="tab-{slug}">\n<p class="lede">{esc(lede)}</p>\n'
                    f'<div class="diagram-container">\n{svg}\n</div>\n</section>')
    js = """
(function () {
  var root = document.documentElement; root.classList.add('js');
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('.panel'));
  function show(i, focus) {
    tabs.forEach(function (t, k) {
      t.setAttribute('aria-selected', k === i ? 'true' : 'false');
      t.tabIndex = k === i ? 0 : -1; panels[k].hidden = k !== i;
    });
    if (focus) tabs[i].focus();
    try { history.replaceState(null, '', '#' + tabs[i].id.replace('tab-', '')); } catch (e) {}
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(i, false); });
    t.addEventListener('keydown', function (e) {
      var k = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 :
              e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1;
      if (k < 0) return; e.preventDefault(); show((k + tabs.length) % tabs.length, true);
    });
  });
  var h = location.hash.replace('#', ''), start = 0;
  tabs.forEach(function (t, i) { if (t.id === 'tab-' + h) start = i; });
  show(start, false);
})();
"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Linutil menu map</title>
  {FONTS}
  <style>{CSS_BASE}{CSS_TABS}</style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Menu map · Tree</p>
    <h1>Linutil menu map</h1>
    <p class="lede">Every top-level tab of the Linutil menu, with its submenus and direct actions. Generated from core/tabs/*/tab_data.toml.</p>
    <div class="tabs" role="tablist" aria-label="Linutil tabs">
      {''.join(buttons)}
    </div>
    {chr(10).join(secs)}
  </div>
  <script>{js}</script>
</body>
</html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    tabs = load()
    total = sum(t['total'] for t in tabs)
    panels = []
    slug, svg, W, title, desc = overview(tabs)
    lede = (f'{total} entries across {len(tabs)} tabs. Each list shows submenus with action '
            f'counts; open a tab for its detail.')
    (OUT / f'{slug}.html').write_text(standalone(slug, f'{title} · Tree', 'Linutil menu overview', lede, svg))
    panels.append((slug, 'Overview', '', lede, svg))
    for t in tabs:
        slug, svg, W, title, desc = tab_diagram(t)
        l = lede_for(t)
        (OUT / f'{slug}.html').write_text(standalone(slug, f'{title} · Tree', f"Linutil menu · {t['name']}", l, svg))
        panels.append((slug, t['name'], str(t['total']), l, svg))
        print(slug, 'W', W)
    (OUT / 'index.html').write_text(wrapper(panels, tabs))
    print('written to', OUT)


if __name__ == '__main__':
    main()
