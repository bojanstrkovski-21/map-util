# Gum menu navigation

These behaviors are in `03` and in `install-scripts/130-archboki-install-apps.sh`. Check the scripts before relying on them, because the map was taken from `master`.

- A submenu choice labeled Back to Main Menu runs `./03.arch-boki-post-install-gum.sh` again. The submenu loop stays underneath. The published map does not list Back or Main Menu on submenus.
- Main Menu choice 4 runs `install-scripts/130-archboki-install-apps.sh` and then exits `03`. It does not return to the Main Menu.
- Inside the apps script, Back to install_apps starts `130` again. Main Menu starts `03` again. Both sit on top of the current menu. Quit ends the apps script, which also ends the `03` that launched it. Quit is listed only on the Main Menu of the published map.
- On-screen choice "Add erik_dubois_repos" calls `add_arco_linux_repos` and runs `add-repos/get-the-arcolinux-keys-and-repos.sh`. The live lines append `[nemesis_repo]`. The ArcoLinux repo blocks in that file are commented out.
- Hyprland is `choose-desktop/hyprland-scripts/00-hyprland-new.sh`. It installs with `yay` and does not enable a display manager.
- App rows are inline `pacman` or `yay` commands. Affine uses `yay -S affine-bin`. Stacer uses `yay -S --needed --noconfirm stacer-bin`. The other rows use `sudo pacman -S --needed --noconfirm`.

Source notes: `archboki-post-map-diagram/post-install-system-map.md`.
