# map-util

An interactive map of the [Linutil](https://github.com/ChrisTitusTech/linutil) menu: every top-level tab, its submenus, and its direct actions, with the script path, task flags and restrictions of each entry. At the time of writing that is 186 entries across 5 tabs.

**Live site:** https://bojanstrkovski-21.github.io/map-util/

The site is published with GitHub Pages from this repository. The repository is also the development environment: it holds the generator scripts that build the pages from Linutil's `core/tabs/*/tab_data.toml` files, and the diagram-design skill used for the diagrams.

## What the site has

- A tab per Linutil tab, each with a diagram of its submenus and direct actions, and a sub-tab view of every entry.
- Search across all entries, with jump-to-row.
- Light and dark themes (dark uses the archboki_nvim palette).
- An About tab with these notes, and the full structure page embedded in it.

## In this repository

| Path | What it is |
| --- | --- |
| `index.html` | The map, the home page of the site |
| `linutil-menu-map/` | The per-tab and full-structure pages, plus `linutil-menu-outline.md`, a text outline of every entry |
| `linutil-menu-map-generator/` | The Python scripts that regenerate the pages and the outline |
| `.claude/`, `.agents/`, `skills-lock.json` | The installed [diagram-design](https://github.com/cathrynlavery/diagram-design) skill |

For the full list of entries without opening the site, see [`linutil-menu-map/linutil-menu-outline.md`](linutil-menu-map/linutil-menu-outline.md).

## Regenerating the pages

The scripts need Python 3.11 or newer (they use `tomllib`) and a clone of Linutil at `linutil/` in the repository root. That folder is gitignored.

```bash
git clone --depth 1 https://github.com/ChrisTitusTech/linutil.git linutil
python3 linutil-menu-map-generator/gen_menu_tree.py
python3 linutil-menu-map-generator/gen_outline.py
```

`gen_menu_tree.py` writes `index.html` and the pages in `linutil-menu-map/`; `gen_outline.py` writes the text outline.

The scripts currently contain absolute paths to the author's machine. To run them elsewhere, change `TABS` (the input, `linutil/core/tabs`) and `OUT` (the output folder) at the top of `gen_menu_map.py`, and `TABS` and `OUT` in `gen_outline.py`.

## Credits

Linutil is by [Chris Titus Tech](https://github.com/ChrisTitusTech/linutil). The diagram styling comes from the diagram-design skill by cathrynlavery.
