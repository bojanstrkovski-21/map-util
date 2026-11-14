#!/usr/bin/env python3
"""Generate a Markdown outline of the Linutil menu from tab_data.toml files."""
import tomllib
from pathlib import Path

TABS = Path('/home/bojan/Projects/diagram/linutil/core/tabs')
OUT = Path('/home/bojan/Projects/diagram/linutil-menu-map/linutil-menu-outline.md')


def leaves(es):
    return sum(leaves(e['entries']) if 'entries' in e else 1 for e in es)


def pre(e):
    out = []
    for p in e.get('preconditions', []):
        vals = ', '.join(str(v) for v in p.get('values', []))
        neg = '' if p.get('matches', True) else 'not '
        d = p.get('data')
        if isinstance(d, dict):
            for kind, arg in d.items():
                out.append(f"{neg}{kind} {arg} in ({vals})")
        else:
            out.append(f"{neg}{d}({vals})")
    return '; '.join(out)


def line(e, depth, inherited_ms):
    ind = '  ' * depth
    ms = e.get('multi_select', True) and inherited_ms
    if 'entries' in e:
        bits = [f"**{e['name']}** ({leaves(e['entries'])} actions)"]
        if not e.get('multi_select', True):
            bits.append('multi_select=false (applies to children)')
        p = pre(e)
        if p:
            bits.append(f'requires: {p}')
        rows = [f"{ind}- {' | '.join(bits)}"]
        for c in e['entries']:
            rows.extend(line(c, depth + 1, ms))
        return rows
    src = f"`{e['script']}`" if 'script' in e else '`command` (inline)'
    bits = [f"{e['name']}", src]
    if e.get('task_list'):
        bits.append(f"flags: {e['task_list']}")
    if not ms:
        bits.append('no multi-select')
    p = pre(e)
    if p:
        bits.append(f'requires: {p}')
    return [f"{ind}- {' | '.join(bits)}"]


def main():
    order = tomllib.load(open(TABS / 'tabs.toml', 'rb'))['directories']
    datas = [(d, tomllib.load(open(TABS / d / 'tab_data.toml', 'rb'))) for d in order]
    total = sum(leaves(t['data']) for _, t in datas)
    md = ['# Linutil menu outline', '',
          f'Generated from `core/tabs/*/tab_data.toml`. {total} entries across {len(datas)} tabs.',
          '', 'Line format: `Name | script path (relative to the tab directory) | task flags | '
          'restrictions`. Flags: D disk, FI flatpak install, FM file modification, I privileged '
          'install, K kernel, MP package manager, RP package removal, SI full system install, '
          'SS service action, P* privileged. Display names matter: `auto_execute` in the config '
          'resolves entries by name.', '']
    for d, t in datas:
        md.append(f"## {t['name']} ({leaves(t['data'])}) - `core/tabs/{d}/`")
        md.append('')
        dirs = [e for e in t['data'] if 'entries' in e]
        loose = [e for e in t['data'] if 'entries' not in e]
        if dirs:
            md.append('### Submenus')
            for e in dirs:
                md.extend(line(e, 0, True))
            md.append('')
        if loose:
            md.append(f'### Direct actions ({len(loose)})')
            for e in loose:
                md.extend(line(e, 0, True))
            md.append('')
    OUT.write_text('\n'.join(md))
    n = sum(1 for l in md if l.lstrip().startswith('- ') and '(' not in l.split('|')[0][:0])
    print('written', OUT, 'total', total)


main()
