#!/usr/bin/env python3
"""Generate the Linutil menu map (HTML/SVG) from core/tabs/*/tab_data.toml."""
import html
import math
import tomllib
from pathlib import Path

TABS = Path('/home/bojan/Projects/diagram/linutil/core/tabs')
OUT = Path('/home/bojan/Projects/diagram/linutil-menu-map')

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
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc" style="min-width:{W}px;max-width:{W}px">\n'
            f'<title id="{slug}-title">{esc(title)}</title>\n'
            f'<desc id="{slug}-desc">{esc(desc)}</desc>\n'
            f'<rect width="100%" height="100%" fill="{C["paper"]}"/>\n'
            f'{body}\n</svg>')


# -------------------------------------------------------------- overview
def overview(tabs):
    slug = 'linutil-overview'
    TW, GAP, n = 208, 16, len(tabs)
    assert n % 2 == 1
    X0 = 40
    row_w = n * TW + (n - 1) * GAP
    W = g4(row_w + 80)
    total = sum(t['total'] for t in tabs)
    root_x = X0 + (row_w - TW) // 2
    root_cx = root_x + TW // 2
    centers = [X0 + TW // 2 + i * (TW + GAP) for i in range(n)]
    ROOT_Y, BUS_Y, TAB_Y, H48 = 40, 112, 136, 48

    conn, nodes, lists = [], [], []
    conn.append(path(f'M {root_cx} {ROOT_Y + H48} V {TAB_Y}'))
    mid = n // 2
    conn.append(path(f'M {root_cx} {BUS_Y} H {centers[0] + 8} Q {centers[0]} {BUS_Y} '
                     f'{centers[0]} {BUS_Y + 8} V {TAB_Y}'))
    conn.append(path(f'M {root_cx} {BUS_Y} H {centers[-1] - 8} Q {centers[-1]} {BUS_Y} '
                     f'{centers[-1]} {BUS_Y + 8} V {TAB_Y}'))
    for i in range(1, n - 1):
        if i != mid:
            conn.append(path(f'M {centers[i]} {BUS_Y} V {TAB_Y}'))

    nodes.append(node(root_x, ROOT_Y, TW, H48, 'Linutil', f'{total} entries · {n} tabs',
                      'root', 'ROOT'))
    bottom = TAB_Y + H48
    for i, t in enumerate(tabs):
        tx = X0 + i * (TW + GAP)
        sub = f"{t['total']} entries"
        if t['folders']:
            sub += f" · {len(t['folders'])} menus"
        nodes.append(node(tx, TAB_Y, TW, H48, t['name'], sub, 'tab', 'TAB'))
        rows = [(f['name'], str(f['leaves']), False) for f in t['folders']]
        if t['loose']:
            rows.append(('Direct actions', str(len(t['loose'])), True))
        railx = tx + 16
        first = TAB_Y + H48 + 20
        last = first + (len(rows) - 1) * 24
        lists.append(f'<line x1="{railx}" y1="{TAB_Y + H48}" x2="{railx}" y2="{last}" '
                     f'stroke="{C["rail"]}" stroke-width="0.8"/>')
        for j, (nm, cnt, direct) in enumerate(rows):
            cy = first + j * 24
            lists.append(f'<line x1="{railx}" y1="{cy}" x2="{railx + 12}" y2="{cy}" '
                         f'stroke="{C["rail"]}" stroke-width="0.8"/>')
            style = ' font-style="italic"' if direct else ''
            col = C['muted'] if direct else C['ink']
            lists.append(text(tx + 32, cy + 4, nm, 11, col, SANS, anchor='start', extra=style))
            lists.append(text(tx + TW - 8, cy + 3, cnt, 9, C['soft'], MONO, anchor='end'))
        bottom = max(bottom, last + 16)
    ly = bottom + 28
    H = ly + 60
    body = '\n'.join(conn + nodes + lists + [legend(
        ly, [('root', 'Root'), ('tab', 'Top-level tab')],
        'Each list: submenus with their action counts; "Direct actions" sit on the tab itself.',
        W)])
    title = 'Linutil menu overview'
    desc = (f'Tree of the Linutil menu: a root with {n} top-level tabs, each listing its '
            f'submenus and a count of direct actions, {total} entries in total.')
    return slug, svg_wrap(slug, title, desc, W, H, body), W, title, desc


# ---------------------------------------------------------------- per tab
def tab_diagram(t):
    slug = f"linutil-{t['dir']}"
    folders, loose = t['folders'], t['loose']
    named = len(loose) <= GROUP_LIMIT
    gname = f'{len(loose)} direct actions'
    gsub = 'grouped · count only'

    labels = [f['name'] for f in folders] + (loose if named else [gname])
    subs = [folder_sub(f) for f in folders] + ([] if named else [gsub])
    NW = g4(max([168] + [tw(l, 12, 0.62) + 32 for l in labels]
                + [tw(s, 9, 0.62) + 32 for s in subs]))
    RW = g4(max(168, tw(t['name'], 12, 0.62) + 32))
    RX, RH = 40, 56
    bx = RX + RW + 32
    ZX = bx + 32
    ZW = 32 + NW

    def zh(rows):
        return 40 + rows * 48 + (rows - 1) * 12 + 16

    zones, nodes, conn = [], [], []
    A = B = Cz = None
    y = 40
    if folders:
        A = dict(x=ZX, y=y, w=ZW, h=zh(len(folders)))
        y = A['y'] + A['h'] + 24
    if loose:
        rows = len(loose) if named else 1
        B = dict(x=ZX, y=y, w=ZW, h=zh(rows))
    entries = [z['y'] + 28 for z in (A, B) if z]

    # root node position
    cy = entries[0] if len(entries) == 1 else g4(sum(entries) / 2)
    ry = cy - RH // 2
    nodes.append(node(RX, ry, RW, RH, t['name'], f"{t['total']} entries", 'root', 'TAB'))
    rx = RX + RW
    zx = ZX
    if len(entries) == 1:
        conn.append(path(f'M {rx} {cy} H {zx}') if cy == entries[0] else '')
    else:
        conn.append(path(f'M {rx} {cy} H {bx}'))
        for ey in entries:
            d = 1 if ey > cy else -1
            conn.append(path(f'M {bx} {cy} V {ey - 8 * d} Q {bx} {ey} {bx + 8} {ey} H {zx}'))

    max_right = ZX + ZW
    max_bottom = ry + RH
    if A:
        zones.append(zone(A['x'], A['y'], A['w'], A['h'], f'SUBMENUS · {len(folders)}'))
        for i, f in enumerate(folders):
            ny = A['y'] + 40 + i * 60
            nodes.append(node(A['x'] + 16, ny, NW, 48, f['name'], folder_sub(f), 'menu', 'MENU'))
            if f['subs']:
                assert Cz is None
                cx0 = A['x'] + A['w'] + 56
                names = [s[0] for s in f['subs']]
                subl = [f'{s[1]} actions' for s in f['subs']]
                CN = g4(max([168] + [tw(l, 12, 0.62) + 32 for l in names]
                            + [tw(s, 9, 0.62) + 32 for s in subl]))
                Cz = dict(x=cx0, y=A['y'], w=32 + CN, h=zh(len(names)))
                ncy = ny + 24
                assert Cz['y'] < ncy < Cz['y'] + Cz['h']
                conn.append(path(f"M {A['x'] + 16 + NW} {ncy} H {Cz['x']}"))
                zones.append(zone(Cz['x'], Cz['y'], Cz['w'], Cz['h'],
                                  f"{f['name'].upper()} · {len(names)} SUBMENUS"))
                for k, (nm, cnt) in enumerate(f['subs']):
                    nodes.append(node(Cz['x'] + 16, Cz['y'] + 40 + k * 60, CN, 48, nm,
                                      f'{cnt} actions', 'menu', 'MENU'))
                max_right = max(max_right, Cz['x'] + Cz['w'])
                max_bottom = max(max_bottom, Cz['y'] + Cz['h'])
        max_bottom = max(max_bottom, A['y'] + A['h'])
    if B:
        zones.append(zone(B['x'], B['y'], B['w'], B['h'], f'DIRECT ACTIONS · {len(loose)}'))
        if named:
            for i, nm in enumerate(loose):
                nodes.append(node(B['x'] + 16, B['y'] + 40 + i * 60, NW, 48, nm, None, 'leaf'))
        else:
            nodes.append(node(B['x'] + 16, B['y'] + 40, NW, 48, gname, gsub, 'group'))
        max_bottom = max(max_bottom, B['y'] + B['h'])

    W = g4(max_right + 40)
    ly = max_bottom + 28
    H = ly + 60
    items = [('root', 'Tab')]
    if A:
        items.append(('menu', 'Submenu'))
    if B:
        items.append(('leaf', 'Direct action') if named else ('group', 'Direct actions (grouped)'))
    body = '\n'.join(zones + [c for c in conn if c] + nodes + [legend(ly, items, None, W)])
    n_menus = len(folders)
    title = f"Linutil menu: {t['name']}"
    parts = []
    if n_menus:
        parts.append(f'{n_menus} submenus')
    if loose:
        parts.append(f'{len(loose)} direct actions')
    desc = (f"Tree of the {t['name']} tab in Linutil, {t['total']} entries across "
            f"{' and '.join(parts)}.")
    return slug, svg_wrap(slug, title, desc, W, H, body), W, title, desc


# ------------------------------------------------------------------ pages
CSS_BASE = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
/*THEME*/
body { font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink);
  min-height: 100vh; padding: 3rem 2rem; }
.frame { max-width: 1280px; width: 100%; margin: 0 auto; }
.eyebrow { font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }
h1 { font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem);
  font-weight: 400; letter-spacing: -0.02em; line-height: 1.15; color: var(--color-ink);
  margin-bottom: 0.5rem; }
.lede { font-size: 0.9rem; color: var(--color-muted); margin-bottom: 1.5rem; max-width: 64ch; }
.diagram-container { width: 100%; overflow-x: auto; }
svg { width: 100%; display: block; }
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
