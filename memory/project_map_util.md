---
name: project-map-util
description: "map-util is one GitHub Pages site for the Linutil map and the Arch-Boki post-install map"
metadata:
  type: project
---

`~/Projects/map-util` (GitHub `bojanstrkovski-21/map-util`, Pages at https://bojanstrkovski-21.github.io/map-util/) is one site for both maps. Do not split them into two repos. The script projects stay separate: Linutil is a gitignored clone at `linutil/`, and the post-install scripts stay in `arch-boki-post-install-dev`.

**Pages.** Root `index.html` is the home ("Menu maps"). No eyebrow. The theme button sits on the title row, top right. The four buttons and the about links open with `target="_blank"`: Linutil map, Arch-Boki map, Linutil GitHub (`ChrisTitusTech/linutil`), Arch-Boki GitHub (`arch-boki-post-install-dev`). The Linutil map itself is `linutil-menu-map/index.html` (186 entries). The Arch-Boki map is `archboki-post-map/index.html` (297 entries). Each map header has Home (same tab), the other map (new tab), and Source repo (new tab). Linutil's Source repo is this repo. Arch-Boki's Source repo is `arch-boki-post-install-dev`. Shared theme key: `linutil-map-theme`.

**Generators.** Do not hand-edit the HTML. `python3 linutil-menu-map-generator/gen_menu_tree.py` writes the home page and the Linutil map. `python3 archboki-post-map/gen_post_map.py` writes the Arch-Boki map and imports `gen_menu_map.py` for colors, fonts, SVG wrap, and base CSS. Diagrams use menu, folder, and script glyphs; branching menus are horizontal blocks; a single-action submenu folds into Direct actions; more than four blocks splits near half (5 becomes 3 and 2); diagrams shrink to about 85 percent, then scroll. Quit stays only on the Arch-Boki main menu. The Arch-Boki About tab is the old "How a choice moves" section.

**Notes.** `archboki-post-map-diagram/` had its own `.git` and its own `memory/`. The `.git` was removed on 2026-11-16 so the markdown can be committed with this repo. The old history remains at https://github.com/bojanstrkovski-21/archboki-post-map-diagram. That `memory/` was merged into this repository's `memory/` the same day. Do not add a second memory folder. Do not commit the `linutil/` clone.

**Publish.** Pages serves the root of `main`. https://bojanstrkovski-21.github.io/map-util/ is still the old Linutil map until this working tree is committed and pushed. A push of the current `origin/main` does not change the site. The commit has to include the untracked `archboki-post-map/`, `archboki-post-map-diagram/`, `linutil-menu-map/index.html`, `memory/`, and `PROJECT.md`. Checked 2026-11-16: no `memory` file or directory remains under either Arch-Boki folder.

**Still stale.** `linutil-menu-map-generator/gen_outline.py` still points `TABS` and `OUT` at `/home/bojan/Projects/diagram/...`.
