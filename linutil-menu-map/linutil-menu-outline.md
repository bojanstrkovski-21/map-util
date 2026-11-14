# Linutil menu outline

Generated from `core/tabs/*/tab_data.toml`. 186 entries across 5 tabs.

Line format: `Name | script path (relative to the tab directory) | task flags | restrictions`. Flags: D disk, FI flatpak install, FM file modification, I privileged install, K kernel, MP package manager, RP package removal, SI full system install, SS service action, P* privileged. Display names matter: `auto_execute` in the config resolves entries by name.

## Applications Setup (74) - `core/tabs/applications-setup/`

### Submenus
- **Communication Apps** (8 actions)
  - Discord | `communication-apps/discord-setup.sh` | flags: I
  - Jitsi | `communication-apps/jitsi-setup.sh` | flags: I
  - Signal | `communication-apps/signal-setup.sh` | flags: I
  - Slack | `communication-apps/slack-setup.sh` | flags: I
  - Telegram | `communication-apps/telegram-setup.sh` | flags: I
  - Thunderbird | `communication-apps/thunderbird-setup.sh` | flags: I
  - ZapZap | `communication-apps/zapzap-setup.sh` | flags: I
  - Zoom | `communication-apps/zoom-setup.sh` | flags: I
- **Design Tools** (17 actions)
  - Ardour | `design-tools/ardour.sh` | flags: I
  - Audacity | `design-tools/audacity.sh` | flags: I
  - Blender | `design-tools/blender.sh` | flags: I
  - Darktable | `design-tools/darktable.sh` | flags: I
  - GNU Image Manipulation Program (GIMP) | `design-tools/gimp.sh` | flags: I
  - Handbrake | `design-tools/handbrake.sh` | flags: I
  - Inkscape | `design-tools/inkscape.sh` | flags: I
  - Krita | `design-tools/krita.sh` | flags: I
  - MyPaint | `design-tools/mypaint.sh` | flags: I
  - Natron | `design-tools/natron.sh` | flags: I
  - OBS Studio | `design-tools/obs-studio.sh` | flags: I
  - Olive | `design-tools/olive.sh` | flags: I
  - OpenShot | `design-tools/openshot.sh` | flags: I
  - Pinta | `design-tools/pinta.sh` | flags: I
  - Scribus | `design-tools/scribus.sh` | flags: I
  - Synfig Studio | `design-tools/synfigstudio.sh` | flags: I
  - Tenacity | `design-tools/tenacity.sh` | flags: I
- **Developer Tools** (10 actions)
  - Cursor | `developer-tools/cursor.sh` | flags: I
  - Github Desktop | `developer-tools/githubdesktop.sh` | flags: I
  - JetBrains Toolbox | `developer-tools/jetbrains-toolbox.sh` | flags: I
  - Meld | `developer-tools/meld.sh` | flags: I FI
  - Neovim | `developer-tools/neovim.sh` | flags: I FM
  - Ngrok | `developer-tools/ngrok.sh` | flags: I
  - Sublime Text | `developer-tools/sublime.sh` | flags: I
  - VS Code | `developer-tools/vscode.sh` | flags: I
  - VS Codium | `developer-tools/vscodium.sh` | flags: I
  - Zed | `developer-tools/zed.sh` | flags: I
- **Office Suites** (4 actions)
  - FreeOffice | `office-suites/freeoffice.sh` | flags: I
  - LibreOffice | `office-suites/libreoffice.sh` | flags: I
  - OnlyOffice | `office-suites/onlyoffice.sh` | flags: I
  - WPS Office | `office-suites/wpsoffice.sh` | flags: I
- **PDF Suites** (4 actions)
  - Evince | `pdf-suites/evince.sh` | flags: I
  - Okular | `pdf-suites/okular.sh` | flags: I
  - PDF Studio | `pdf-suites/pdfstudio.sh` | flags: I
  - PDF Studio Viewer | `pdf-suites/pdfstudioviewer.sh`
- **Web Browsers** (13 actions)
  - Brave | `browsers/brave.sh` | flags: I
  - Brave Origin | `browsers/brave-origin.sh` | flags: I
  - Chromium | `browsers/chromium.sh` | flags: I
  - Google Chrome | `browsers/google-chrome.sh` | flags: I
  - LibreWolf | `browsers/librewolf.sh` | flags: I
  - Lynx | `browsers/lynx.sh` | flags: I
  - Mozilla Firefox | `browsers/firefox.sh` | flags: I
  - Thorium | `browsers/thorium.sh` | flags: I
  - Tor Browser | `browsers/tor-browser.sh` | flags: I
  - Vivaldi | `browsers/vivaldi.sh` | flags: I
  - waterfox | `browsers/waterfox.sh` | flags: FI
  - Zen Browser | `browsers/zen-browser.sh` | flags: I
  - Helium Browser | `browsers/helium-browser.sh` | flags: I

### Direct actions (18)
- Alacritty | `alacritty-setup.sh` | flags: I FM
- Android Debloater | `android-debloat.sh` | flags: I
- Bash Prompt | `mybash-setup.sh` | flags: I FM
- Dank Shell | `dank-shell.sh` | flags: I FM
- Docker | `docker-setup.sh` | flags: I SS
- Fastfetch | `fastfetch-setup.sh` | flags: I FM
- Flatpak / Flathub | `setup-flatpak.sh` | flags: I
- Ghostty | `ghostty-setup.sh` | flags: I FM
- Grub Theme | `grub-theme.sh` | flags: PFM
- Kitty | `kitty-setup.sh` | flags: I FM
- Linutil Installer | `linutil-installer.sh` | flags: I | requires: not command_exists(linutil)
- Linutil Updater | `linutil-updater.sh` | flags: I | requires: command_exists(linutil)
- Noctalia Shell | `noctalia-shell.sh` | flags: I FM
- Podman | `podman-setup.sh` | flags: I SS
- Podman-compose | `podman-compose-setup.sh` | flags: I SS
- Rofi | `rofi-setup.sh` | flags: I FM
- Shelly | `shelly-setup.sh` | flags: I SS | requires: command_exists(pacman)
- ZSH Prompt | `zsh-setup.sh` | flags: I FM

## Gaming (36) - `core/tabs/gaming/`

### Submenus
- **Emulators** (18 actions)
  - **Multi-System Emulators** (2 actions)
    - RetroArch Game Emulator | `emulators/retroarch.sh` | flags: FM
    - RetroArch Cores | `emulators/retroarch-cores.sh` | flags: I | no multi-select
  - **Nintendo Emulators** (8 actions)
    - bsnes | `emulators/nintendo/bsnes.sh` | flags: FM
    - Dolphin Emulator | `emulators/nintendo/dolphin-emu.sh` | flags: FM
    - Gopher 64 | `emulators/nintendo/gopher64.sh` | flags: FM
    - MelonDS | `emulators/nintendo/melonds.sh` | flags: FM
    - mGBA | `emulators/nintendo/mgba.sh` | flags: FM
    - Mupen 64 Plus | `emulators/nintendo/mupen64plus.sh` | flags: FM
    - Ryujinx | `emulators/nintendo/ryujinx.sh` | flags: FM
    - snes9x | `emulators/nintendo/snes9x.sh` | flags: FM
  - **PlayStation Emulators** (3 actions)
    - PCSX2 | `emulators/playstation/pcsx2.sh` | flags: FM
    - Play! | `emulators/playstation/play-emu.sh` | flags: FM
    - RPCS3 | `emulators/playstation/rpcs3.sh` | flags: FM
  - **Sega Emulators** (3 actions)
    - Blastem | `emulators/sega/blastem.sh` | flags: FM
    - Flycast | `emulators/sega/flycast.sh` | flags: FM
    - Kronos | `emulators/sega/kronos.sh` | flags: FM
  - **Xbox Emulators** (2 actions)
    - XEMU | `emulators/xbox/xemu.sh` | flags: FM
    - Xenia | `emulators/xbox/xenia.sh` | flags: FM
- **Game Launchers** (4 actions)
  - Heroic | `heroic-launcher.sh` | flags: FI
  - Lutris | `lutris-launcher.sh` | flags: FI
  - RetroArch | `retroarch-launcher.sh` | flags: FI
  - Steam | `steam-launcher.sh` | flags: FI
- **Tools and Setups** (9 actions)
  - Auto CPU Frequency | `../applications-setup/auto-cpufreq.sh` | flags: I SS
  - Auto Mount Drive | `../utils/auto-mount.sh` | flags: PFM | no multi-select
  - Bottles | `../applications-setup/bottles-setup.sh` | flags: FI
  - Gaming Dependencies | `../system-setup/gaming-setup.sh` | flags: I
  - General GPU Drivers | `../system-setup/gpu-driver.sh` | flags: I | no multi-select
  - Nvidia Drivers & Hardware Acceleration | `../system-setup/arch/nvidia-drivers.sh` | flags: I
  - ProtonPlus | `protonplus.sh` | flags: FI
  - ProtonUp-Qt | `protonup-qt.sh` | flags: FI
  - Waydroid | `../applications-setup/waydroid-setup.sh` | flags: I SS | requires: environment XDG_SESSION_TYPE in (wayland, Wayland)

### Direct actions (5)
- Arc Raiders Titus Mods | `arc-raiders-mod.sh` | flags: FM
- Diablo II Resurrected Loot Filter | `diablo2-titus-mod.sh` | flags: FM
- EverQuest Legends MIDI Fix | `eq-legends-midi.sh` | flags: I MP FM | no multi-select | requires: command_exists(curl, flock, lutris, mkfifo, pgrep, ps, python3, sha256sum, stat); not command_exists(apk)
- Fallout 76 INI and Mods | `fallout76-titus-mod.sh` | flags: FM
- Starfield Titus INI and Mods | `starfield-titus-mod.sh` | flags: FM

## Security (4) - `core/tabs/security/`

### Direct actions (4)
- FirewallD Firewall Baselines (CTT) | `firewalld-baselines.sh` | flags: I SS | requires: command_exists(firewall-cmd)
- Lynis Security Audit | `lynis-audit.sh` | flags: I MP RP | no multi-select
- rkhunter Rootkit Scan | `rkhunter-scan.sh` | flags: I MP RP | no multi-select
- UFW Firewall Baselines (CTT) | `ufw-baselines.sh` | flags: I SS | requires: not command_exists(firewall-cmd)

## System Setup (37) - `core/tabs/system-setup/`

### Submenus
- **Alpine** (1 actions) | requires: command_exists(apk)
  - Alpine Update | `alpine/alpine-upgrade.sh` | flags: P MP | no multi-select
- **Arch** (14 actions) | requires: command_exists(pacman)
  - Arch Server Setup | `arch/server-setup.sh` | flags: SI D | no multi-select
  - DWM-Titus | `arch/dwmtitus-setup.sh` | flags: I PFM SS
  - Hyprland JaKooLit | `arch/hyprland-kool.sh` | flags: I MP | no multi-select
  - Install CachyOS Repository and Kernel | `arch/cachyos-repos.sh` | flags: I K RP | no multi-select
  - Install Chaotic-AUR Repository | `arch/chaotic-aur-setup.sh` | flags: I
  - Linux Neptune for SteamDeck | `arch/linux-neptune.sh` | flags: I PFM K | requires: containing_file /sys/devices/virtual/dmi/id/board_vendor in (Valve)
  - Nvidia Drivers & Hardware Acceleration | `arch/nvidia-drivers.sh` | flags: I FM SS
  - Omarchy Rice by DHH | `arch/omarchy.sh` | flags: I MP | no multi-select
  - Pacman Config | `arch/pacman-config.sh` | flags: PFM
  - Paru AUR Helper | `arch/paru-setup.sh` | flags: I
  - Snapper Snapshots | `arch/snapshot-setup.sh` | flags: I PFM SS | requires: command_exists(btrfs)
  - System Maintenance | `arch/system-maintenance.sh` | flags: PFM RP
  - Virtualization | `arch/virtualization.sh` | flags: FM I SS RP
  - Yay AUR Helper | `arch/yay-setup.sh` | flags: I
- **Debian** (1 actions) | requires: containing_file /etc/os-release in (ID=debian)
  - Hyprland JaKooLit | `debian/hyprland-kool-deb.sh` | flags: I MP
- **Desktop Environment Setup** (2 actions)
  - Install Desktop Environment | `desktop-environments.sh` | flags: I
  - Uninstall Desktop Environment | `desktop-environments-uninstall.sh` | flags: RP
- **Fedora** (8 actions) | requires: command_exists(dnf); command_exists(btrfs)
  - Btrfs Assistant, Snapper Config, grub-btrfs | `fedora/fedora-btrfs-assistant.sh` | flags: I PFM SS
  - Configure DNF | `fedora/configure-dnf.sh` | flags: PFM
  - Hyprland JaKooLit | `fedora/hyprland-kool-fed.sh` | flags: I MP
  - Multimedia Codecs | `fedora/multimedia-codecs.sh` | flags: I
  - Nvidia Proprietary Drivers | `fedora/nvidia-proprietary-driver-setup.sh` | flags: I
  - RPM Fusion | `fedora/rpm-fusion-setup.sh` | flags: MP | no multi-select
  - Upgrade to a New Fedora Release | `fedora/fedora-upgrade.sh` | flags: MP
  - Virtualization | `fedora/virtualization.sh` | flags: I
- **Ubuntu** (1 actions) | requires: containing_file /etc/os-release in (ID=ubuntu); containing_file /etc/os-release in (VERSION_ID="24.04")
  - Hyprland JaKooLit | `ubuntu/hyprland-kool-ubuntu24.sh` | flags: I MP

### Direct actions (10)
- Build Prerequisites | `compile-setup.sh` | flags: I
- Enable SSD TRIM | `fstrim-setup.sh` | flags: D I SS | no multi-select | requires: command_exists(systemctl)
- Full System Cleanup | `system-cleanup.sh` | flags: RP PFM | no multi-select
- Full System Update | `system-update.sh` | flags: PFM | no multi-select
- Full System Update (Topgrade) | `system-update-topgrade.sh` | flags: PFM | no multi-select
- Global Theme | `global-theme.sh` | flags: I PFM
- PipeWire Audio | `pipewire-setup.sh` | flags: I
- Remove Snaps | `remove-snaps.sh` | flags: RP
- TTY Fonts | `terminus-tty.sh` | flags: I PFM
- Zram Swap | `zram-setup.sh` | flags: PFM

## Utilities (35) - `core/tabs/utils/`

### Submenus
- **Monitor Control** (12 actions) | multi_select=false (applies to children) | requires: environment XDG_SESSION_TYPE in (x11, X11, xorg, Xorg, tty); environment DISPLAY in (:0, :1, :2, :3, :4, :5, :6, :7, :8, :9)
  - Auto Detect Displays | `monitor-control/auto_detect_displays.sh` | no multi-select
  - Change Orientation | `monitor-control/change_orientation.sh` | no multi-select
  - Disable Monitor | `monitor-control/disable_monitor.sh` | no multi-select
  - Duplicate Displays | `monitor-control/duplicate_displays.sh` | no multi-select
  - Enable Monitor | `monitor-control/enable_monitor.sh` | no multi-select
  - Extend Displays | `monitor-control/extend_displays.sh` | no multi-select
  - Manage Arrangement | `monitor-control/manage_arrangement.sh` | no multi-select
  - Reset Scaling | `monitor-control/reset_scaling.sh` | no multi-select
  - Scale Monitors | `monitor-control/scale_monitor.sh` | no multi-select
  - Set Brightness | `monitor-control/set_brightness.sh` | no multi-select
  - Set Primary Monitor | `monitor-control/set_primary_monitor.sh` | no multi-select
  - Set Resolution | `monitor-control/set_resolutions.sh` | no multi-select
- **Printers** (3 actions)
  - CUPS | `printers/install-cups.sh` | flags: I
  - Epson printer drivers | `printers/install-epson-printer-drivers.sh` | flags: I
  - HP printer drivers | `printers/install-hp-printer-drivers.sh` | flags: I
- **User Account Manager** (5 actions) | multi_select=false (applies to children)
  - Add User | `user-account-manager/add_user.sh` | no multi-select
  - Add User To Groups | `user-account-manager/add_to_group.sh` | no multi-select
  - Change Password | `user-account-manager/change_password.sh` | no multi-select
  - Delete User | `user-account-manager/delete_user.sh` | no multi-select
  - Remove User From Groups | `user-account-manager/remove_from_group.sh` | no multi-select

### Direct actions (15)
- Auto Login | `auto-login.sh` | flags: DE setup
- Bluetooth Manager | `bluetooth-control.sh` | flags: I SS | no multi-select
- Bootable USB Creator | `create-bootable-usb.sh` | flags: D
- Crypto tool | `encrypt_decrypt_tool.sh` | flags: I FM
- Locale Setup | `locale-setup.sh` | flags: FM | requires: command_exists(locale-gen)
- Numlock on Startup | `numlock.sh` | flags: PFM SS
- Ollama | `ollama.sh` | flags: I SS
- Ramalama | `ramalama.sh` | flags: I SS
- Ramalama Model Manager | `ramalama-models.sh` | no multi-select
- Service Manager | `service-control.sh` | flags: I PFM SS
- SSH Commands | `ssh.sh` | flags: I FM SS
- SSH Samba | `samba-ssh-setup.sh` | flags: I SS PFM
- Timeshift Backup | `timeshift.sh` | flags: I | requires: not command_exists(dnf)
- US Locale Setup | `locale-us-setup.sh` | flags: FM
- WiFi Manager | `wifi-control.sh` | flags: I SS
