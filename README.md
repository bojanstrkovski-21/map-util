# map-util

Home page for two menu maps. The [Linutil](https://github.com/ChrisTitusTech/linutil) map lists every tab, submenu, and direct action (186 entries across 5 tabs). The Arch-Boki map lists every menu opened by `03.arch-boki-post-install-gum.sh` (297 entries).

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
| `index.html` | Home page for both maps |
| `linutil-menu-map/` | The Linutil map (`index.html`), the per-tab and full-structure pages, plus `linutil-menu-outline.md` |
| `linutil-menu-map-generator/` | The Python scripts that regenerate the pages and the outline |
| `archboki-post-map/` | The same kind of map for the Arch-Boki post-install gum menu. Open `archboki-post-map/index.html` |
| `.claude/`, `.agents/`, `skills-lock.json` | The installed [diagram-design](https://github.com/cathrynlavery/diagram-design) skill |

For the full list of entries without opening the site, see [`linutil-menu-map/linutil-menu-outline.md`](linutil-menu-map/linutil-menu-outline.md).

## Regenerating the pages

The scripts need Python 3.11 or newer (they use `tomllib`) and a clone of Linutil at `linutil/` in the repository root. That folder is gitignored.

```bash
git clone --depth 1 https://github.com/ChrisTitusTech/linutil.git linutil
python3 linutil-menu-map-generator/gen_menu_tree.py
python3 linutil-menu-map-generator/gen_outline.py
```

`gen_menu_tree.py` writes the home page at `index.html` and the Linutil map in `linutil-menu-map/`; `gen_outline.py` writes the text outline. The Arch-Boki map is `python3 archboki-post-map/gen_post_map.py`.

`gen_menu_map.py` and `gen_menu_tree.py` find Linutil and the output folder from the repository root. `gen_outline.py` still has absolute paths under `/home/bojan/Projects/diagram/` and needs those two constants changed before it will run here.

## Credits

Linutil is by [Chris Titus Tech](https://github.com/ChrisTitusTech/linutil). The diagram styling comes from the diagram-design skill by cathrynlavery.
