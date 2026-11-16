# map-util

## Overview

One GitHub Pages site for two menu maps. The root page introduces both. The Linutil map covers Chris Titus Tech's Linutil (186 entries). The Arch-Boki map covers `03.arch-boki-post-install-gum.sh` (297 entries).

## Stack

- **Language**: Python 3.11+ (`tomllib`) generators, static HTML
- **Framework / Tools**: no site framework; GitHub Pages
- **Key dependencies**: a gitignored clone of Linutil at `linutil/`

## Conventions

Generated HTML is not edited by hand. `gen_menu_tree.py` writes the home page and `linutil-menu-map/`. `archboki-post-map/gen_post_map.py` writes the Arch-Boki page and imports `gen_menu_map.py` for the shared look. External links and the home-page map buttons use `target="_blank"`. Home on a map page stays in the same tab.

## Constraints

Keep both maps in this repository. Do not commit `linutil/`. Do not put a nested `.git` back inside `archboki-post-map-diagram/`. Quit is listed only on the Arch-Boki main menu.

## Frozen Files

None.

## How to Run

```bash
git clone --depth 1 https://github.com/ChrisTitusTech/linutil.git linutil
python3 linutil-menu-map-generator/gen_menu_tree.py
python3 archboki-post-map/gen_post_map.py
```

## Current State

Root `index.html` is the home page locally. The Linutil map is `linutil-menu-map/index.html`. The Arch-Boki map is `archboki-post-map/index.html`. Theme key `linutil-map-theme` is shared. Pages serves the root of `main`. The live site is still the old Linutil map. Nothing from this work is committed. One memory folder: `memory/` at the repo root. `gen_outline.py` still has absolute paths under `/home/bojan/Projects/diagram/`.

## Next Steps

- Commit and push so Pages serves the home page and both maps.
- Point `gen_outline.py` at the repo-relative Linutil clone and regenerate the outline.

## Recent Work

- 2026-11-16 — Home page for both maps, shared diagram style, nested git and nested memory removed from `archboki-post-map-diagram/`. Live Pages still shows the old home until commit and push.
