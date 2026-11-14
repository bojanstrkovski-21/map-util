#!/usr/bin/env python3
"""Add sub-tab full-structure views, search and how-to to the Linutil menu map.

Reuses gen_menu_map.py (diagrams) and writes every page in the output folder.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mm', HERE / 'gen_menu_map.py')
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)
esc = mm.esc

FLAG_NAMES = {
    'D': 'Disk modification', 'FI': 'Flatpak installation', 'FM': 'File modification',
    'I': 'Privileged installation', 'K': 'Kernel modification',
    'MP': 'Package manager action', 'RP': 'Package removal',
    'SI': 'Full system installation', 'SS': 'Service or systemd action',
}


def flag_title(tok):
    if tok in FLAG_NAMES:
        return FLAG_NAMES[tok]
    if tok.startswith('P') and tok[1:] in FLAG_NAMES:
        return 'Privileged: ' + FLAG_NAMES[tok[1:]]
    return tok


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


def action_row(e, aid, multi_ok):
    src = e.get('script')
    code = f'<code>{esc(src)}</code>' if src else '<code class="inline">inline command</code>'
    chips = [f'<span class="chip" title="{esc(flag_title(tok))}">{esc(tok)}</span>'
             for tok in e.get('task_list', '').split()]
    if not multi_ok:
        chips.append('<span class="chip alt" title="Cannot be queued with other commands">no multi-select</span>')
    p = pre(e)
    if p:
        chips.append(f'<span class="chip alt" title="Entry is hidden unless this holds">requires: {esc(p)}</span>')
    return (f'<li class="row" id="a-{aid}"><span class="nm">{esc(e["name"])}</span>{code}'
            f'<span class="chips">{"".join(chips)}</span></li>')


# ----------------------------------------------------------- sub-tab tree
def build_tree(tab, recs, ctr):
    def rows_for(entries, crumb, ms):
        rows = []
        for e in entries:
            if 'entries' in e:
                continue
            ctr['a'] += 1
            aid = ctr['a']
            ok = e.get('multi_select', True) and ms
            rows.append(action_row(e, aid, ok))
            recs.append(dict(id=aid, tab=tab['name'], slug=tab['dir'], crumb=crumb,
                             name=e['name'], script=e.get('script') or 'inline command',
                             flags=e.get('task_list', '')))
        return '<ul class="rows">' + ''.join(rows) + '</ul>'

    def notes(e):
        out = ''
        if not e.get('multi_select', True):
            out += '<span class="chip alt">no multi-select (applies to everything inside)</span>'
        p = pre(e)
        if p:
            out += f'<span class="chip alt">requires: {esc(p)}</span>'
        return f'<p class="panelnotes">{out}</p>' if out else ''

    def subgroup(items):
        """items: (label, count, notes_html, inner_html); first item is selected."""
        btns, panels = [], []
        for i, (label, count, note, inner) in enumerate(items):
            ctr['p'] += 1
            k = ctr['p']
            sel = 'true' if i == 0 else 'false'
            btns.append(f'<button type="button" class="subtab" role="tab" id="st-{k}" aria-controls="sp-{k}" '
                        f'aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{esc(label)}'
                        f'<span class="n">{count}</span></button>')
            panels.append(f'<div class="subpanel" role="tabpanel" id="sp-{k}" aria-labelledby="st-{k}">'
                          f'<h3 class="sub">{esc(label)} · {count}</h3>{note}{inner}</div>')
        return (f'<div class="subgroup"><div class="subtabs" role="tablist">{"".join(btns)}</div>'
                f'{"".join(panels)}</div>')

    def content(e, crumb, ms):
        kids = e['entries']
        ms2 = ms and e.get('multi_select', True)
        cr = crumb + [e['name']]
        loose = [c for c in kids if 'entries' not in c]
        dirs = [c for c in kids if 'entries' in c]
        if not dirs:
            return rows_for(loose, cr, ms2)
        items = []
        if loose:
            items.append(('Actions', len(loose), '', rows_for(loose, cr, ms2)))
        for d in dirs:
            items.append((d['name'], mm.leaves(d['entries']), notes(d), content(d, cr, ms2)))
        return subgroup(items)

    raw = tab['raw']
    items = []
    loose = [e for e in raw if 'entries' not in e]
    if loose:
        items.append(('Direct actions', len(loose), '', rows_for(loose, [], True)))
    for e in raw:
        if 'entries' in e:
            items.append((e['name'], mm.leaves(e['entries']), notes(e), content(e, [], True)))
    return subgroup(items)


def tree_section(t, recs, ctr, heading='Full structure'):
    body = build_tree(t, recs, ctr)
    return (f'<section class="tree" aria-label="{esc(t["name"])} full structure">\n'
            f'<h2>{esc(heading)}</h2>\n'
            f'<p class="note">Edit <code>core/tabs/{t["dir"]}/tab_data.toml</code>. Scripts live under '
            f'<code>core/tabs/{t["dir"]}/</code>; paths below are relative to that folder. Chips are task '
            f'flags (hover for the meaning) and restrictions.</p>\n'
            f'<div class="toolbar"><button type="button" data-act="showall">Show all</button></div>\n'
            f'{body}\n</section>')


SEARCH = """<div class="search">
<label for="q">Find an entry</label>
<input id="q" type="search" placeholder="name, script or flag, e.g. docker, .sh, FM" autocomplete="off">
<p class="count" id="qc" aria-live="polite"></p>
<ul class="results" id="qr"></ul>
</div>"""


def howto():
    flags = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in FLAG_NAMES.items())
    return f"""<section class="howto">
<h2>Adding, changing or removing an entry</h2>
<p class="note">Summarized from the repository's SPEC.md and AGENTS.md.</p>
<ol>
<li><strong>Script.</strong> Put it under <code>core/tabs/&lt;tab&gt;/</code>. Use POSIX sh (<code>#!/bin/sh -e</code>), source <code>common-script.sh</code> with the right number of <code>..</code>, and call <code>checkEnv</code> before relying on <code>PACKAGER</code>, <code>ESCALATION_TOOL</code>, <code>ARCH</code> or <code>DTYPE</code>.</li>
<li><strong>Menu entry.</strong> Add or edit it in that tab's <code>tab_data.toml</code>: <code>name</code>, <code>description</code>, exactly one of <code>script</code>, <code>command</code> or <code>entries</code>, plus <code>task_list</code>, <code>preconditions</code> and <code>multi_select</code> as needed. A submenu is an entry with <code>entries</code>.</li>
<li><strong>New top-level tab.</strong> A new directory with its own <code>tab_data.toml</code>, plus a line in <code>core/tabs/tabs.toml</code>. The order there is the tab order.</li>
<li><strong>Remove.</strong> Delete the entry from <code>tab_data.toml</code> and its script if nothing else uses it.</li>
<li><strong>Afterwards.</strong> Run <code>cargo xtask docgen</code> when entries or descriptions changed, <code>cargo test --no-fail-fast --package linutil_core</code>, and ShellCheck on changed scripts.</li>
</ol>
<p class="note"><strong>Watch out.</strong> Config <code>auto_execute</code> resolves entries by display name, so renaming breaks existing configs. <code>multi_select = false</code> on a parent applies to all its children; use it for destructive, interactive or rebooting entries. Preconditions only hide an entry, so scripts must still validate their own requirements.</p>
<h3 class="sub">Task flags</h3>
<dl class="flags">{flags}<dt>P*</dt><dd>Prefix P marks the action as needing privileges</dd></dl>
</section>"""


CSS_TREE = """
.tree, .howto, .search { margin-top: 2.5rem; max-width: 1100px; }
.tree h2, .howto h2, .diagramh { font: 400 1.4rem var(--font-serif); letter-spacing: -0.01em; margin-bottom: 0.25rem; }
.tree { margin-top: 0; }
.diagramh { margin: 2.5rem 0 0.75rem; }
.note { font-size: 0.82rem; color: var(--color-muted); margin-bottom: 1rem; max-width: 72ch; }
code { font-family: var(--font-mono); font-size: 0.74rem; }
h3.sub { font: 500 0.66rem var(--font-mono); letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--color-muted); margin: 1.5rem 0 0.5rem; }
.toolbar { display: none; gap: 0.5rem; margin: 0.75rem 0 0.25rem; }
.js .toolbar { display: flex; }
.toolbar button { font: 500 0.72rem var(--font-sans); border: 1px solid var(--color-rule);
  background: none; border-radius: 6px; padding: 0.3rem 0.65rem; color: var(--color-ink); cursor: pointer; }
.toolbar button:hover { background: var(--color-paper-2); }
.subtabs { display: none; flex-wrap: wrap; gap: 0.25rem; border-bottom: 1px solid var(--color-rule); margin: 1rem 0 0.75rem; }
.js .subtabs { display: flex; }
.js .tree.all .subtabs { display: none; }
.subtab { font: 500 0.8rem var(--font-sans); color: var(--color-muted); background: none; border: 0;
  border-bottom: 2px solid transparent; padding: 0.5rem 0.8rem; cursor: pointer; margin-bottom: -1px; }
.subtab .n { font-family: var(--font-mono); font-size: 0.66rem; color: var(--color-soft); margin-left: 0.4rem; }
.subtab:hover { color: var(--color-ink); }
.subtab[aria-selected="true"] { color: var(--color-ink); border-bottom-color: var(--color-ink); }
.subtab:focus-visible, .toolbar button:focus-visible, .results button:focus-visible, #q:focus-visible {
  outline: 2px solid var(--color-accent); outline-offset: 2px; }
.subpanel { background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 8px;
  padding: 0.25rem 0.9rem 0.5rem; margin-bottom: 0.75rem; }
.subpanel .subgroup .subpanel { background: var(--color-paper); margin: 0.5rem 0; }
.subpanel > h3.sub { margin-top: 0.75rem; }
.js .subpanel > h3.sub { display: none; }
.js .tree.all .subpanel > h3.sub { display: block; }
.js .subpanel[hidden] { display: none; }
.js .tree.all .subpanel[hidden] { display: block; }
.panelnotes { margin: 0.5rem 0 0.25rem; }
ul.rows { list-style: none; padding: 0; }
.nm { font-weight: 600; font-size: 0.88rem; }
.row { display: grid; grid-template-columns: minmax(170px, 1.2fr) minmax(200px, 1.6fr) 2fr; gap: 0.75rem;
  align-items: baseline; padding: 0.45rem 0.25rem; border-top: 1px solid var(--color-rule); }
.row:first-child { border-top: 0; }
.row.flash { outline: 2px solid var(--color-accent); outline-offset: 1px; background: var(--color-tint); }
.row code.inline { color: var(--color-soft); font-style: italic; }
.chip { display: inline-block; font: 500 0.65rem var(--font-mono); border: 1px solid var(--color-chip-ink);
  border-radius: 4px; padding: 0.05rem 0.35rem; margin: 0 0.3rem 0.2rem 0; overflow-wrap: anywhere; }
.row > *, .results button > * { min-width: 0; overflow-wrap: anywhere; }
.chip.alt { border-style: dashed; color: var(--color-muted); }
.search { display: none; }
.js .search { display: block; position: relative; margin-top: 0; margin-bottom: 1.5rem; max-width: 720px; }
.search label { font: 500 0.66rem var(--font-mono); letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--color-muted); display: block; margin-bottom: 0.4rem; }
#q { width: 100%; max-width: 560px; font: 400 0.9rem var(--font-sans); padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-rule); border-radius: 6px; background: var(--color-paper-2); color: var(--color-ink); }
.count { position: absolute; top: 0; right: 0; margin: 0; font: 400 0.72rem var(--font-mono);
  line-height: 1; color: var(--color-soft); }
.results { list-style: none; position: absolute; left: 0; right: 0; top: 100%; z-index: 20;
  max-height: 60vh; overflow-y: auto; background: var(--color-paper-2);
  border: 1px solid var(--color-rule); border-radius: 8px; }
.results:empty { display: none; }
.results button { display: grid; grid-template-columns: minmax(0, 1fr); gap: 0.1rem; width: 100%;
  text-align: left; font: inherit; color: inherit; background: none; border: 0;
  border-top: 1px solid var(--color-rule); padding: 0.55rem 0.8rem; cursor: pointer; }
.results li:first-child button { border-top: 0; }
.results button:hover { background: var(--color-paper-2); }
.crumb { font-size: 0.78rem; color: var(--color-muted); }
.howto ol { margin: 0.75rem 0 1rem 1.25rem; font-size: 0.86rem; max-width: 80ch; }
.howto li { margin-bottom: 0.45rem; line-height: 1.5; }
.flags { display: grid; grid-template-columns: 3rem 1fr; gap: 0.2rem 0.75rem; font-size: 0.82rem; max-width: 520px; }
.flags dt { font: 500 0.72rem var(--font-mono); }
.fulltab { margin-top: 3rem; }
.topbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.topactions { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.btn { display: inline-block; font: 500 0.72rem var(--font-sans); border: 1px solid var(--color-rule);
  background: none; border-radius: 6px; padding: 0.35rem 0.7rem; color: var(--color-ink);
  text-decoration: none; white-space: nowrap; }
.btn:hover { background: var(--color-paper-2); }
.btn:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
.btn.primary { font-size: 0.82rem; padding: 0.5rem 0.9rem; border-color: var(--color-muted); }
.docs { max-width: 100%; }
.docs .note, .docs .actions, .docs .docsrepo { max-width: 760px; }
.embedpanel { padding: 0; background: none; border: 0; }
.embedpanel > h3.sub { margin-bottom: 0.5rem; }
.embedpanel iframe { display: block; width: 100%; height: 80vh; min-height: 520px;
  border: 1px solid var(--color-rule); border-radius: 8px; background: var(--color-paper); }
.embed body { padding: 1rem 1.25rem; min-height: 0; }
.embed .topbar, .embed .frame > .lede { display: none; }
.embed .frame { max-width: none; }
.docs a:not(.btn) { color: var(--color-ink); }
.docs .actions { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1rem 0 0.5rem; }
.docsrepo { grid-template-columns: minmax(180px, 14rem) 1fr; max-width: 640px; }
.themebtn { display: none; font: 500 0.72rem var(--font-sans); border: 1px solid var(--color-rule);
  background: none; border-radius: 6px; padding: 0.35rem 0.7rem; color: var(--color-ink);
  cursor: pointer; white-space: nowrap; }
.js .themebtn { display: inline-block; }
.themebtn:hover, .themebtn[aria-pressed="true"] { background: var(--color-paper-2); }
.themebtn:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
@media (max-width: 720px) {
  .row, .results button { grid-template-columns: minmax(0, 1fr); gap: 0.15rem; }
}
"""

JS = """
(function () {
  document.documentElement.classList.add('js');
  if (/[?&]embed\\b/.test(location.search)) document.documentElement.classList.add('embed');
  var tb = document.getElementById('themebtn');
  if (tb) {
    var root = document.documentElement;
    var cur = function () {
      return root.getAttribute('data-theme') ||
        (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    };
    var paint = function () {
      var d = cur() === 'dark';
      tb.setAttribute('aria-pressed', d ? 'true' : 'false');
      tb.textContent = d ? 'Dark mode: on' : 'Dark mode: off';
    };
    tb.addEventListener('click', function () {
      var next = cur() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('linutil-map-theme', next); } catch (e) {}
      paint(); syncFrame();
    });
    paint();
    var fs = document.getElementById('fsframe');
    function syncFrame() {
      if (!fs) return;
      try {
        var d = fs.contentDocument;
        if (d && d.documentElement) d.documentElement.setAttribute('data-theme', cur());
      } catch (e) {}
    }
    if (fs) fs.addEventListener('load', syncFrame);
  }
  var tabs =[].slice.call(document.querySelectorAll('.tab'));
  var panels = [].slice.call(document.querySelectorAll('.panel'));
  function show(i, focus) {
    tabs.forEach(function (t, k) {
      t.setAttribute('aria-selected', k === i ? 'true' : 'false');
      t.tabIndex = k === i ? 0 : -1; panels[k].hidden = k !== i;
    });
    if (focus) tabs[i].focus();
    try { history.replaceState(null, '', '#' + tabs[i].id.replace('tab-', '')); } catch (e) {}
  }
  if (tabs.length) {
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i, false); });
      t.addEventListener('keydown', function (e) {
        var k = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 :
                e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1;
        if (k < 0) return; e.preventDefault(); show((k + tabs.length) % tabs.length, true);
      });
    });
    var h = location.hash.replace('#', ''), start = 0;
    tabs.forEach(function (t, i) { if (t.hasAttribute('data-default')) start = i; });
    tabs.forEach(function (t, i) { if (t.id === 'tab-' + h) start = i; });
    show(start, false);
  }

  function kids(el, cls) {
    return [].filter.call(el.children, function (c) { return c.classList.contains(cls); });
  }
  function selectSub(btn, focus) {
    var group = btn.closest('.subgroup');
    var bar = kids(group, 'subtabs')[0];
    [].forEach.call(bar.children, function (b) {
      var on = b === btn;
      b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1;
    });
    kids(group, 'subpanel').forEach(function (p) { p.hidden = p.id !== btn.getAttribute('aria-controls'); });
    if (focus) btn.focus();
  }
  [].forEach.call(document.querySelectorAll('.subgroup'), function (g) {
    var bar = kids(g, 'subtabs')[0], btns = [].slice.call(bar.children);
    btns.forEach(function (b, i) {
      b.addEventListener('click', function () { selectSub(b, false); });
      b.addEventListener('keydown', function (e) {
        var k = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 :
                e.key === 'Home' ? 0 : e.key === 'End' ? btns.length - 1 : -1;
        if (k < 0) return; e.preventDefault(); selectSub(btns[(k + btns.length) % btns.length], true);
      });
    });
    selectSub(btns[0], false);
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-act="showall"]') : null;
    if (!b) return;
    var scope = b.closest('.tree'); if (!scope) return;
    var all = scope.classList.toggle('all');
    b.textContent = all ? 'Show one at a time' : 'Show all';
  });

  var q = document.getElementById('q'), list = document.getElementById('qr'),
      cnt = document.getElementById('qc'), data = [];
  try { data = JSON.parse(document.getElementById('entries').textContent); } catch (e) {}
  function jump(id, slug) {
    var ti = -1; tabs.forEach(function (t, i) { if (t.id === 'tab-linutil-' + slug) ti = i; });
    if (ti >= 0) show(ti, false);
    var el = document.getElementById('a-' + id); if (!el) return;
    var chain = [];
    for (var p = el.parentElement; p; p = p.parentElement) if (p.classList.contains('subpanel')) chain.unshift(p);
    chain.forEach(function (pn) { var b = document.getElementById(pn.getAttribute('aria-labelledby')); if (b) selectSub(b, false); });
    el.scrollIntoView({ block: 'center' });
    el.classList.add('flash'); setTimeout(function () { el.classList.remove('flash'); }, 2200);
  }
  function render() {
    var terms = q.value.toLowerCase().split(/\\s+/).filter(Boolean);
    list.innerHTML = ''; if (!terms.length) { cnt.textContent = ''; return; }
    var hits = data.filter(function (r) {
      var s = (r.name + ' ' + r.script + ' ' + r.flags + ' ' + r.tab + ' ' + r.crumb.join(' ')).toLowerCase();
      return terms.every(function (t) { return s.indexOf(t) >= 0; });
    });
    cnt.textContent = hits.length + (hits.length === 1 ? ' match' : ' matches') + (hits.length > 40 ? ', showing 40' : '');
    hits.slice(0, 40).forEach(function (r) {
      var li = document.createElement('li'), b = document.createElement('button');
      b.type = 'button';
      var n = document.createElement('span'); n.className = 'nm'; n.textContent = r.name;
      var c = document.createElement('span'); c.className = 'crumb';
      c.textContent = [r.tab].concat(r.crumb).join(' \\u203a ');
      var s = document.createElement('code'); s.textContent = r.script;
      b.appendChild(n); b.appendChild(c); b.appendChild(s);
      b.addEventListener('click', function () { jump(r.id, r.slug); list.innerHTML = ''; cnt.textContent = ''; });
      li.appendChild(b); list.appendChild(li);
    });
  }
  if (q) {
    q.addEventListener('input', render);
    q.addEventListener('focus', function () { if (q.value) render(); });
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape') { q.value = ''; render(); } });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.search')) { list.innerHTML = ''; cnt.textContent = ''; }
    });
  }
})();
"""


def data_script(recs):
    j = json.dumps(recs, ensure_ascii=False).replace('</', '<\\/')
    return f'<script type="application/json" id="entries">{j}</script>'


EARLY = ("<script>try{var t=localStorage.getItem('linutil-map-theme');"
         "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}"
         "catch(e){}</script>")
THEME_BTN = '<button type="button" class="themebtn" id="themebtn" aria-pressed="false">Dark mode</button>'
GH_URL = 'https://github.com/bojanstrkovski-21/map-util'
TOP_ACTIONS = (f'<div class="topactions"><a class="btn" href="{GH_URL}" target="_blank" '
               f'rel="noopener">GitHub</a>{THEME_BTN}</div>')


DEFAULT_TAB = 'about'


def about_html():
    about = f"""<p class="note">This is the Linutil menu map, published with GitHub Pages from the
<a href="{GH_URL}" target="_blank" rel="noopener">map-util</a> repository. The repository is also the
development environment: it holds the generator scripts that build these pages from Linutil's
<code>core/tabs/*/tab_data.toml</code>, and the diagram-design skill used for the diagrams.</p>
<p class="actions"><a class="btn primary" href="{GH_URL}" target="_blank" rel="noopener">View on GitHub</a></p>
<h3 class="sub">In the repository</h3>
<dl class="flags docsrepo">
<dt>linutil-menu-map/</dt><dd>These pages, plus a text outline of every entry</dd>
<dt>linutil-menu-map-generator/</dt><dd>The Python scripts that regenerate them</dd>
<dt>.claude/, .agents/</dt><dd>The installed diagram-design skill</dd>
</dl>"""
    full = ('<iframe id="fsframe" title="Linutil full structure" loading="lazy" '
            'src="linutil-full-structure.html?embed=1"></iframe>')
    items = [('About', about), ('Full structure', full)]
    btns, panels = [], []
    for i, (label, inner) in enumerate(items, 1):
        sel = 'true' if i == 1 else 'false'
        btns.append(f'<button type="button" class="subtab" role="tab" id="st-about{i}" aria-controls="sp-about{i}" '
                    f'aria-selected="{sel}" tabindex="{0 if i == 1 else -1}">{esc(label)}</button>')
        cls = 'subpanel embedpanel' if label == 'Full structure' else 'subpanel'
        panels.append(f'<div class="{cls}" role="tabpanel" id="sp-about{i}" aria-labelledby="st-about{i}">'
                      f'<h3 class="sub">{esc(label)}</h3>{inner}</div>')
    return (f'<section class="docs"><div class="subgroup"><div class="subtabs" role="tablist">{"".join(btns)}</div>'
            f'{"".join(panels)}</div></section>')


def head(title, css, js=False):
    early = EARLY if js else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  {early}
  {mm.FONTS}
  <style>{css}</style>
</head>
<body>
  <div class="frame">"""


def body_order(svg, extra, extra_first):
    if svg is None:
        return extra
    diagram = f'<div class="diagram-container">\n{svg}\n</div>'
    if extra_first:
        return f'{extra}\n<h2 class="diagramh">Diagram</h2>\n{diagram}'
    return f'{diagram}\n{extra}'


def standalone(title, h1, lede, svg, extra='', extra_first=False):
    return (head(title, mm.CSS_BASE + CSS_TREE) + f"""
    <p class="eyebrow">Menu map · Tree</p>
    <h1>{esc(h1)}</h1>
    <p class="lede">{esc(lede)}</p>
{body_order(svg, extra, extra_first)}
  </div>
</body>
</html>
""")


def wrapper(panels, recs):
    buttons, secs = [], []
    for i, (slug, label, count, lede, svg, extra, first) in enumerate(panels):
        is_def = slug == DEFAULT_TAB
        sel = 'true' if is_def else 'false'
        n = f'<span class="n">{count}</span>' if count else ''
        buttons.append(f'<button class="tab" role="tab" id="tab-{slug}" aria-controls="panel-{slug}" '
                       f'aria-selected="{sel}" tabindex="{0 if is_def else -1}"'
                       f'{" data-default" if is_def else ""}>{esc(label)}{n}</button>')
        secs.append(f'<section class="panel" role="tabpanel" id="panel-{slug}" aria-labelledby="tab-{slug}">\n'
                    f'<p class="lede">{esc(lede)}</p>\n{body_order(svg, extra, first)}\n</section>')
    return (head('Linutil menu map', mm.CSS_BASE + mm.CSS_TABS + CSS_TREE, True) + f"""
    <div class="topbar"><div>
    <p class="eyebrow">Menu map · Tree</p>
    <h1>Linutil menu map</h1></div>{TOP_ACTIONS}</div>
    <p class="lede">Every top-level tab of the Linutil menu, with its submenus and direct actions. Generated from core/tabs/*/tab_data.toml.</p>
    {SEARCH}
    <div class="tabs" role="tablist" aria-label="Linutil tabs">
      {''.join(buttons)}
    </div>
    {chr(10).join(secs)}
  </div>
  {data_script(recs)}
  <script>{JS}</script>
</body>
</html>
""")


def fullpage(tabs, trees, recs):
    total = sum(t['total'] for t in tabs)
    parts = [head('Linutil full structure', mm.CSS_BASE + CSS_TREE, True), f"""
    <div class="topbar"><div>
    <p class="eyebrow">Menu map · Tree</p>
    <h1>Linutil full structure</h1></div>{TOP_ACTIONS}</div>
    <p class="lede">All {total} entries across {len(tabs)} tabs, with script paths, task flags and restrictions. Generated from core/tabs/*/tab_data.toml.</p>
    {SEARCH}
    {howto()}"""]
    for t in tabs:
        parts.append(f'<div class="fulltab" id="{t["dir"]}">{trees[t["dir"]]}</div>')
    parts.append(f'  </div>\n  {data_script(recs)}\n  <script>{JS}</script>\n</body>\n</html>\n')
    return '\n'.join(parts)


def main():
    mm.OUT.mkdir(exist_ok=True)
    tabs = mm.load()
    total = sum(t['total'] for t in tabs)
    recs, ctr = [], {'a': 0, 'p': 0}
    trees = {t['dir']: tree_section(t, recs, ctr, t['name']) for t in tabs}
    recs2, ctr2 = [], {'a': 0, 'p': 0}
    plain = {t['dir']: tree_section(t, recs2, ctr2, 'Full structure') for t in tabs}

    panels = []
    slug, svg, W, title, desc = mm.overview(tabs)
    lede = (f'{total} entries across {len(tabs)} tabs. Each list shows submenus with action '
            f'counts; open a tab for its diagram and full structure.')
    (mm.OUT / f'{slug}.html').write_text(
        standalone(f'{title} · Tree', 'Linutil menu overview', lede, svg))
    panels.append((slug, 'Overview', '', lede, svg, howto(), False))
    for t in tabs:
        slug, svg, W, title, desc = mm.tab_diagram(t)
        l = mm.lede_for(t)
        (mm.OUT / f'{slug}.html').write_text(
            standalone(f'{title} · Tree', f"Linutil menu · {t['name']}", l, svg, plain[t['dir']], True))
        panels.append((slug, t['name'], str(t['total']), l, svg, plain[t['dir']], True))
    panels.append((DEFAULT_TAB, 'About', '', 'About this site and where it lives.', None,
                   about_html(), False))
    (mm.OUT / 'index.html').write_text(wrapper(panels, recs2))
    (mm.OUT / 'linutil-full-structure.html').write_text(fullpage(tabs, trees, recs))
    print('entries indexed:', len(recs), len(recs2), 'expected', total)


if __name__ == '__main__':
    main()
