#!/usr/bin/env python3
"""Build archboki-post-map/index.html from the post-install menu map.

Source of the entries: ../archboki-post-map-diagram/post-install-system-map.md
Visual system: the Linutil map in this repository (gen_menu_map.py).
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location(
    'mm', ROOT / 'linutil-menu-map-generator' / 'gen_menu_map.py')
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)
esc = mm.esc

OUT = HERE / 'index.html'
SRC = 'https://github.com/bojanstrkovski-21/arch-boki-post-install-dev'
MAP_MD = '../archboki-post-map-diagram/post-install-system-map.md'

KIND_TITLE = {
    'action': 'Runs a script or command, then shows this menu again',
    'menu': 'Clears the screen and opens the next menu',
    'pick': 'Pick list: numbers, a or all, b back, q quit',
    'nested': 'Starts another copy of a script on top of this menu',
    'exit': 'Runs exit and ends that process',
    'return': 'Leaves this script and returns to the menu under it',
}
TOOL_TITLE = {
    'pacman': 'sudo pacman -S --needed --noconfirm, unless the detail says otherwise',
    'yay': 'Installed with yay',
    'script': 'A separate script on the path',
    'inline': 'A command inside 03, not its own script',
}

EXTRA_CSS = """
.detail { display: block; margin-top: 0.2rem; font-size: 0.78rem; color: var(--color-muted); line-height: 1.45; }
.flags.wide { grid-template-columns: 6.5rem 1fr; max-width: 760px; }
.links { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 0.25rem 0 1rem; }
.glyph { width: 0.95rem; height: 0.95rem; flex: none; color: var(--color-ink); }
.nm { display: flex; align-items: center; gap: 0.4rem; }
.subtab { display: inline-flex; align-items: center; gap: 0.35rem; }
h3.sub { display: flex; align-items: center; gap: 0.35rem; }
.js .tree.all .subpanel > h3.sub { display: flex; }
h3.sub .glyph { width: 0.8rem; height: 0.8rem; }
.frame { max-width: 1440px; }
.diagram-container { display: flex; flex-direction: column; gap: 1.75rem; }
.diagram-container svg { height: auto; }
"""

JS = r"""
(function () {
  document.documentElement.classList.add('js');
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
      paint();
    });
    paint();
  }
  var tabs = [].slice.call(document.querySelectorAll('.tabs > .tab'));
  var panels = [].slice.call(document.querySelectorAll('.frame > .panel'));
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
    var ti = -1; tabs.forEach(function (t, i) { if (t.id === 'tab-' + slug) ti = i; });
    if (ti >= 0) show(ti, false);
    var el = document.getElementById('a-' + id); if (!el) return;
    var chain = [];
    for (var p = el.parentElement; p; p = p.parentElement) if (p.classList.contains('subpanel')) chain.unshift(p);
    chain.forEach(function (pn) {
      var b = document.getElementById(pn.getAttribute('aria-labelledby')); if (b) selectSub(b, false);
    });
    el.scrollIntoView({ block: 'center' });
    el.classList.add('flash'); setTimeout(function () { el.classList.remove('flash'); }, 2200);
  }
  function render() {
    var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
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
      c.textContent = [r.tab].concat(r.crumb).join(' \u203a ');
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


def row(name, target, kind='action', detail=None, tool=None):
    item = {'name': name, 'target': target, 'kind': kind}
    if detail:
        item['detail'] = detail
    if tool:
        item['tool'] = tool
    return item


def pkg(name, packages, detail=None, tool='pacman'):
    return row(name, packages, 'action', detail, tool)


def sec(label, rows=None, note=None, children=None):
    return {'label': label, 'rows': rows or [], 'note': note, 'children': children or []}


def main_tail(items):
    return list(items)


def apps_tail(items):
    return list(items)


def pkgs(pairs):
    return [pkg(name, packages) for name, packages in pairs]


# ---------------------------------------------------------------- data
REGULAR_FONTS = [
    'ttf-croscore', 'ttf-carlito', 'ttf-caladea', 'opendesktop-fonts', 'inter-font',
    'ttf-opensans', 'terminus-font', 'freetype2', 'ttf-ms-fonts', 'ttf-mac-fonts',
    'ttf-macedonian-ancient', 'ttf-macedonian-church', 'ttf-material-design-iconic-font',
    'otf-font-awesome', 'ttf-font-awesome-6', 'noto-fonts', 'noto-fonts-cjk',
    'noto-fonts-emoji', 'noto-fonts-extra', 'ttf-anonymous-pro', 'ttf-cascadia-code',
    'ttf-dejavu', 'ttf-fantasque-sans-mono', 'ttf-fira-mono', 'ttf-fira-sans',
    'ttf-fira-code', 'ttf-hack', 'ttf-hellvetica', 'ttf-jetbrains-mono', 'ttf-joypixels',
    'ttf-roboto', 'ttf-roboto-mono', 'ttf-ubuntu-font-family',
]
NERD_FONTS = [
    'CascadiaCode', 'CascadiaMono', 'DejaVuSansMono', 'DroidSansMono', 'FantasqueSansMono',
    'FiraCode', 'FiraMono', 'GeistMono', 'Hack', 'Iosevka', 'JetBrainsMono', 'Lilex',
    'Meslo', 'Mononoki', 'NerFontsSymbolsOnly', 'Noto', 'Overpass', 'RobotoMono',
    'SourceCodePro', 'SpaceMono', 'Ubuntu', 'UbuntuMono', 'UbuntuSans', 'VictorMono',
]

UPDATE_ROWS = main_tail([
    row('Refresh Mirrors', 'add-repos/upd_servers.sh', 'action',
        'That file is sudo pacman -Syyv.', 'script'),
    row('Update System', 'sudo pacman -Syyu', 'action',
        'Run inside 03. No separate script.', 'inline'),
    row('Add arch-boki Repos', 'add-repos/append_archboki_repo.sh', 'action',
        'Appends [shtrkce-repo] (https://bojanstrkovski-21.github.io/$repo/$arch) and '
        '[shtrkce_repo_xl] (https://gitlab.com/bojanstrkovski-21/$repo/-/raw/main/$arch) to '
        '/etc/pacman.conf. Both are SigLevel = Optional TrustAll. Then pacman -Syy.', 'script'),
    row('Add erik_dubois_repos', 'add-repos/get-the-arcolinux-keys-and-repos.sh', 'action',
        'Function name in 03 is add_arco_linux_repos. The ArcoLinux repo blocks in that file '
        'are commented out. Live code appends [nemesis_repo], SigLevel = Never, server '
        'https://erikdubois.github.io/$repo/$arch, then pacman -Syy.', 'script'),
    row('Add Chaotic_repos', 'add-repos/install_and_append_chaotic_repo_and_keyrings.sh', 'action',
        'Receives Chaotic key 3056513887B78AEB, installs chaotic-keyring and chaotic-mirrorlist, '
        'appends [chaotic-aur] with Include = /etc/pacman.d/chaotic-mirrorlist, then pacman -Syy.',
        'script'),
    row('Fix pacman_db_and_keys', 'add-repos/fix-pacman-databases-and-keys.sh', 'action',
        'If 8.8.8.8 answers, installs archlinux-keyring. Wipes /var/lib/pacman/sync/* and '
        '/etc/pacman.d/gnupg/*, runs pacman-key --init and --populate, adds the Ubuntu keyserver, '
        'then pacman -Sy.', 'script'),
    row('Install archlinux-tweak-tool (add nemesis repo first!)',
        'sudo pacman -S archlinux-tweak-tool-git', 'action',
        'Run inside 03. No --needed and no --noconfirm.', 'inline'),
])

DESKTOP_ROWS = main_tail([
    row('Kde - Plasma', 'choose-desktop/kde-plasma/install-kde-plasma.sh', 'action',
        'Installs neovim, sublime-text-4, xed, the plasma group, sddm, sddm-conf, an explicit KF6 '
        'package list, the qt6 group, kvantum, and KDE apps (kdeconnect, dolphin, gwenview, okular, '
        'spectacle, ark, kate, konsole, kcalc, kde-sdk tools). kdenlive is commented out. Then '
        'systemctl enable --now sddm and systemctl start --now sddm.', 'script'),
    row('Xfce', 'choose-desktop/xfce/install-xfce-and-sddm.sh', 'action',
        'Installs xfce4, xfce4-goodies, artwork, screensaver, mugshot, accountsservice, sddm, '
        'sddm-conf, neovim, sublime-text-4, xed, Arco/Arch-Boki themes and wallpapers, '
        'archboki-xfce-git, xfce4-panel-profiles, xfce4-docklike-plugin. Then '
        'systemctl enable sddm.service --now.', 'script'),
    row('Cinnamon', 'choose-desktop/cinnamon/install_cinnamon.sh', 'action',
        'Installs cinnamon, translations, gnome-screenshot, gnome-system-monitor, gnome-terminal, '
        'xfce4-terminal, iso-flag-png, mintlocale, nemo-fileroller, editors, mugshot, '
        'accountsservice, sddm, sddm-conf, and the same theme set as Xfce. Then '
        'systemctl enable sddm.service --now.', 'script'),
    row('Hyprland', 'choose-desktop/hyprland-scripts/00-hyprland-new.sh', 'action',
        'One yay -S --noconfirm --needed per package: Hyprland plus hypridle, hyprlock, hyprpicker, '
        'hyprpolkitagent, hyprshell, hyprshot, hyprsunset, waybar, swaync, swww, walker, rofi-wayland, '
        'portals, and a large app/font stack (terminals, firefox, brave, thunar, neovim, obs, gimp, '
        'sddm, rustup). No display manager is enabled. yay must already be installed.', 'yay'),
])

CORE_MENU = main_tail([
    row('Cpu Check and Install Microcode', 'core-utils/microcode.sh', 'action',
        'No menu. Reads lscpu Vendor ID. GenuineIntel installs intel-ucode. AuthenticAMD installs '
        'amd-ucode. Anything else prints the vendor and exits 1. The install command is '
        'pacman -Syu --noconfirm, so the system upgrades. The initramfs is not rebuilt.', 'script'),
    row('Install GPU Drivers', 'core-utils/gpu-drivers.sh', 'action',
        'No menu. Looks at lspci for a VGA or 3D line that mentions nvidia or amd, and uses field 5 '
        'as the vendor. NVIDIA installs nvidia-dkms nvidia-utils nvidia-settings. AMD installs '
        'xf86-video-amdgpu. Anything else exits 1. Same pacman -Syu upgrade. No Intel path.', 'script'),
    row('Install Audio Drivers', 'core-utils/audio-drivers.sh', 'action',
        'Runs the script, then a 1/2 prompt. If jack2 is installed it is removed with pacman -Rdd '
        'before the prompt. -Rdd skips dependency checks.', 'script'),
    row('Install Bluetooth Drivers', 'install-scripts/123-bluetooth.sh', 'action',
        'Installs pacutils, then pacinstall --resolve-conflicts=all for bluez, bluez-libs, '
        'bluez-utils, blueman. Enables and starts bluetooth.service. Sets AutoEnable=true in '
        '/etc/bluetooth/main.conf.', 'script'),
    row('Install Network Drivers', 'install-scripts/126-network.sh', 'action',
        'Removes iptables with pacman -Rdd, then installs iptables-nft, networkmanager, '
        'networkmanager-openvpn, networkmanager-openconnect, network-manager-applet, '
        'nm-connection-editor, nftables, avahi, samba, NFS packages, the gvfs-* backends, '
        'nss-mdns, file-roller, webkit2gtk. Does not enable NetworkManager.', 'script'),
    row('Install Printer Drivers', 'install-scripts/124-printers.sh', 'action',
        'Installs pacutils, then pacinstall for cups, cups-pdf, cups-browsed, cups-filters, '
        'bluez-cups, ghostscript, gsfonts, gutenprint, foomatic-db-gutenprint-ppds, libcups, '
        'system-config-printer. Enables and starts cups.service.', 'script'),
    row('Install Fonts', 'install-scripts/125-installfont-new.sh', 'menu',
        'Replaces the gum screen with Font Installation Manager. Leaving that script returns to this '
        'Core Utils menu. It does not stack another 03.', 'script'),
    row('Install Core Utils', 'install-scripts/118-core.sh', 'action',
        'No menu. One pacman -S --needed --noconfirm of base, base-devel, linux-headers, dkms, git, '
        'cmake, devtools, archiso and ISO tools, fwupd, fzf, ripgrep, plocate, flatpak, yad, zenity, '
        'xdg-utils, udisks2, and archive tools (p7zip, unrar, unzip, unace).', 'script'),
])

AUDIO_ROWS = [
    row('PipeWire', 'pipewire pipewire-audio pipewire-pulse pipewire-alsa pipewire-jack '
        'pipewire-zeroconf wireplumber pavucontrol', 'action',
        'pacman -Rdd removes the PulseAudio stack and a wide alsa/gstreamer/ffmpeg set, then '
        'installs that multimedia set again plus the PipeWire packages.', 'pacman'),
    row('PulseAudio', 'pulseaudio pulseaudio-alsa pulseaudio-bluetooth pulseaudio-equalizer '
        'pulseaudio-jack pulseaudio-zeroconf pavucontrol', 'action',
        'The reverse. Removes the PipeWire stack with pacman -Rdd, then installs the PulseAudio set.',
        'pacman'),
    row('Anything else', 'exit 1', 'exit', 'Prints Invalid choice. Exiting.'),
]

FONT_MENU = [
    row('Install Regular Fonts', 'sudo pacman -S --needed --noconfirm', 'pick',
        'Opens the regular-font pick list, then pacman, then sudo fc-cache -f -v.'),
    row('Install Nerd Fonts', 'nerd-fonts v3.4.0 zip', 'pick',
        'Opens the nerd-font pick list, then a GitHub zip download.'),
    row('Install Both (Regular Fonts + Nerd Fonts)', 'regular list, then nerd list', 'pick',
        'The regular pick list, then the nerd pick list.'),
]

REGULAR_ROWS = [
    pkg(name, name, 'sudo pacman -S --needed --noconfirm, then sudo fc-cache -f -v.')
    for name in REGULAR_FONTS
]
NERD_ROWS = [
    row(name, f'https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/{name}.zip',
        'pick',
        f'Downloaded into $HOME/.local/share/fonts/{name}, then fc-cache -f. '
        'A font directory that already has files is skipped.', 'script')
    for name in NERD_FONTS
]


def menu_rows(pairs):
    return [row(name, opens, 'menu') for name, opens in pairs]


APPS_TOP = [
    row('File Managers', 'menu file_managers', 'menu'),
    row('Terminal Emulators', 'menu terminal_emulators', 'menu'),
    row('Text editors,pdf, office, dev_tools', 'menu text_devt_office_pdf', 'menu'),
    row('Internet', 'menu internet', 'menu'),
    row('Multimedia', 'menu multimedia', 'menu'),
    row('Graphics', 'menu graphics', 'menu'),
    row('System Info/Monitoring', 'menu system_info', 'menu'),
    row('System Tools', 'menu system_tools', 'menu'),
]

MAIN_ROWS = [
    row('Update and Refresh', 'menu update_and_refresh', 'menu'),
    row('Choose Desktop', 'menu choose_desktop', 'menu'),
    row('Install Core Utils and Drivers', 'menu install_core_utils', 'menu'),
    row('Install Apps', 'install-scripts/130-archboki-install-apps.sh', 'menu',
        'Runs the apps script, then 03 exits with that script\'s status. You do not return to the Main Menu.'),
    row('Quit Arch-Boki post install', 'exit 0', 'exit', 'Ends this process. Quit is only listed here.'),
]

FILE_ROWS = apps_tail(pkgs([
    ('Nemo file manager', 'nemo nemo-compare nemo-fileroller nemo-image-converter nemo-preview nemo-share'),
    ('PcmanFM-gtk3', 'pcmanfm-gtk3'),
    ('PcmanFM-qt', 'pcmanfm-qt'),
    ('Thunar file manager', 'thunar thunar-archive-plugin thunar-shares-plugin thunar-volman tumbler file-roller'),
    ('Nautilus - gnome files', 'nautilus nautilus-share sushi nautilus-code-git nautilus-open-any-terminal'),
    ('Dolphin - Kde Plasma', 'dolphin dolphin-plugins'),
    ('Yazi-Terminal', 'yazi'),
    ('Ranger-Terminal', 'ranger'),
]))
TERM_ROWS = apps_tail(pkgs([
    ('Alacritty', 'alacritty alacritty-themes imagemagick libsixel lsix'),
    ('Ghostty', 'ghostty libsixel imagemagick lsix'),
    ('Kitty', 'kitty kitty-shell-integration libsixel lsix imagemagick'),
    ('tilix', 'tilix'),
    ('Wezterm', 'wezterm-nightly-bin imagemagick'),
    ('Xfce4-Terminal', 'xfce4-terminal'),
]))
EDITOR_ROWS = apps_tail(pkgs([
    ('Emacs', 'emacs'),
    ('Geany', 'geany geany-plugins'),
    ('Leafpad (Lxde)', 'leafpad'),
    ('Mousepad (Xfce)', 'mousepad'),
    ('Sublime-text-4', 'sublime-text-4'),
    ('Xed (Linux Mint)', 'xed'),
]))
OFFICE_ROWS = apps_tail(pkgs([
    ('LibreOffice', 'libreoffice-fresh'),
    ('OnlyOffice', 'onlyoffice'),
]))
MD_ROWS = apps_tail([
    pkg('Affine', 'affine-bin', 'yay -S affine-bin. No --needed and no --noconfirm.', 'yay'),
    pkg('Obsidian', 'obsidian'),
    pkg('Qownnotes', 'qownnotes'),
])
PDF_ROWS = apps_tail(pkgs([
    ('Evince', 'evince'), ('Okular', 'okular'), ('Xpdf', 'xpdf'),
    ('Xreader', 'xreader'), ('Zathura', 'zathura'),
]))
DEV_ROWS = apps_tail(pkgs([
    ('Code', 'code'),
    ('Meld', 'meld'),
    ('Notepadqq', 'notepadqq'),
    ('Pycharm-community-edition', 'pycharm-community-edition'),
    ('Vscodium', 'vscodium vscodium-marketplace'),
    ('Visual Studio Code', 'visual-studio-code-bin'),
    ('Zed', 'zed'),
]))
TEXT_MENU = apps_tail(menu_rows([
    ('Text editors', 'menu text_editors'),
    ('Office suites', 'menu office_suites'),
    ('Markdown editors', 'menu markdown_editors'),
    ('Pdf viewers', 'menu pdf_viewers'),
    ('Dev Tools', 'menu devtools'),
]))
COMM_ROWS = apps_tail(pkgs([
    ('Discord', 'discord'),
    ('Signal', 'signal-desktop'),
    ('Telegram', 'telegram-desktop'),
]))
BROWSER_ROWS = apps_tail(pkgs([
    ('Brave', 'brave-bin'),
    ('Chromium', 'chromium'),
    ('Firefox', 'firefox'),
    ('Firefox-esr', 'firefox-esr'),
    ('Google Chrome', 'google-chrome'),
    ('Librewolf', 'librewolf'),
    ('Qutebrowser', 'qutebrowser'),
    ('Vivaldi', 'vivaldi vivaldi-ffmpeg-codecs'),
]))
DOWN_ROWS = apps_tail(pkgs([
    ('Deluge-Gtk', 'deluge-gtk'),
    ('Ktorrent', 'ktorrent'),
    ('Qbittorrent', 'qbittorrent'),
    ('Transmission-Gtk', 'transmission-gtk'),
    ('Transmission-Qt', 'transmission-qt'),
]))
REC_ROWS = apps_tail(pkgs([
    ('Gpu-screen-recorder-gtk', 'gpu-screen-recorder gpu-screen-recorder-gtk'),
    ('Hyprshot (hyprland-onmly)', 'hyprshot'),
    ('Kazam', 'kazam'),
    ('Obs-studio', 'obs-studio'),
    ('Peek', 'peek'),
    ('Simplescreenrecorder', 'simplescreenrecorder-qt6-git'),
]))
NET_MENU = apps_tail(menu_rows([
    ('Communication/Social', 'menu comunication'),
    ('Web browsers', 'menu web_browsers'),
    ('Downloaders', 'menu downloaders'),
    ('Recorders', 'menu recorders'),
]))
APLAYER_ROWS = apps_tail(pkgs([
    ('Amberol', 'amberol'),
    ('Audacious', 'audacious audacious-plugins'),
    ('Deadbeef', 'deadbeef'),
    ('Elisa', 'elisa'),
    ('G4music', 'g4music-git'),
    ('juk', 'juk'),
    ('lollypop', 'lollypop'),
    ('Pragha', 'pragha'),
    ('Rhythmbox', 'rhythmbox'),
    ('Sayonara Player', 'sayonara-player'),
    ('Strawberry', 'strawberry'),
]))
VPLAYER_ROWS = apps_tail([
    pkg('Celluloid', 'celluloid'),
    pkg('Clapper', 'clapper clapper-enhancers'),
    pkg('Kodi', 'kodi'),
    pkg('Mpv', 'mpv'),
    pkg('Smplayer', 'smplayer smplayer-skins smplayer-themes'),
    pkg('Vlc media player', 'vlc',
        'Plus the vlc-plugin-* set in that case line (codecs, inputs, and outputs).'),
])
AEDIT_ROWS = apps_tail(pkgs([
    ('Ardour', 'ardour'),
    ('Audacity', 'audacity'),
    ('Kwave', 'kwave'),
    ('Lmms', 'lmms'),
    ('Openshot', 'openshot'),
    ('soundconverter', 'soundconverter'),
    ('reaper', 'reaper reapack sws'),
    ('tenacity', 'tenacity'),
]))
VEDIT_ROWS = apps_tail(pkgs([
    ('flowblade', 'flowblade'),
    ('handbrake', 'handbrake'),
    ('kdenlive', 'kdenlive'),
    ('losslesscut', 'losslesscut-bin'),
    ('makemkv', 'makemkv mkvtoolnix-cli mkvtoolnix-gui'),
    ('Openshot', 'openshot'),
    ('Shotcut', 'shotcut'),
]))
SUB_ROWS = apps_tail(pkgs([
    ('Aegisub', 'aegisub'),
    ('Subtitleedit', 'subtitleedit'),
    ('Subtitlecomposer', 'subtitlecomposer'),
]))
MEDIA_MENU = apps_tail(menu_rows([
    ('Audio Players', 'menu audio_players'),
    ('Video Players', 'menu video_players'),
    ('Audio Editors', 'menu audio_editors'),
    ('Video Editors', 'menu video_editors'),
    ('Subtitle Editors', 'menu subtitle_editors'),
]))
VIEW_ROWS = apps_tail(pkgs([
    ('Darktable', 'darktable'),
    ('Ephoto', 'ephoto'),
    ('GPicView', 'gpicview'),
    ('Gwenview', 'gwenview'),
    ('Nomacs', 'nomacs'),
    ('Nsxiv', 'nsxiv'),
    ('Qimgv', 'qimgv-git'),
    ('Ristretto', 'ristretto'),
]))
EDIT_ROWS = apps_tail(pkgs([
    ('Gimp', 'gimp'),
    ('Gpick', 'gpick'),
    ('Inkscape', 'inkscape'),
    ('Krita', 'krita'),
    ('Pinta', 'pinta'),
    ('RawTherapee', 'rawtherapee'),
    ('Upscayl', 'upscayl-desktop-git upscayl-models-desktop'),
]))
WALL_ROWS = apps_tail(pkgs([
    ('Azote(nwg creators)', 'azote'),
    ('Feh(terminal)', 'feh'),
    ('Hyprpaper(hyprland)', 'hyprpaper'),
    ('Nitrogen', 'nitrogen'),
    ('Swaybg(terminal-wayland', 'swaybg'),
    ('Swww(terminal)', 'swww'),
    ('Variety', 'variety'),
    ('Waypaper(wayland-x11-gui)', 'waypaper-git'),
    ('Xwallpaper(terminal)', 'xwallpaper'),
]))
GFX_MENU = apps_tail(menu_rows([
    ('Photo/Image Viewers', 'menu photo_viewers'),
    ('Photo/Image Editors', 'menu photo_editors'),
    ('Wallpaper/Backround Changer', 'menu wallpaper_changer'),
]))
INFO_ROWS = apps_tail([
    pkg('Bashtop', 'bashtop'),
    pkg('Btop', 'btop'),
    pkg('Countryfetch', 'countryfetch'),
    pkg('Cpufetch', 'cpufetch'),
    pkg('Fastfetch', 'fastfetch'),
    pkg('Glances', 'glances'),
    pkg('Gtop', 'gtop'),
    pkg('Htop', 'htop'),
    pkg('Hyfetch', 'hyfetch'),
    pkg('Mission Center', 'mission-center'),
    pkg('Nvtop', 'nvtop'),
    pkg('Resources', 'resources'),
    pkg('Stacer', 'stacer-bin', 'yay -S --needed --noconfirm stacer-bin', 'yay'),
    pkg('Xfce4-Taskmanager', 'xfce4-taskmanager'),
])
LAUNCH_ROWS = apps_tail(pkgs([
    ('Bemenu', 'bemenu'),
    ('Bemenu-Wayland', 'bemenu-wayland'),
    ('Dmenu(it is better to clone and build)', 'dmenu'),
    ('Fuzzel', 'fuzzel'),
    ('Rofi', 'rofi'),
    ('Rofi-Wayland', 'rofi-wayland'),
    ('Tofi', 'tofi'),
    ('Walker', 'walker-bin'),
    ('Wofi', 'wofi'),
]))
CALC_ROWS = apps_tail(pkgs([
    ('Galculator', 'galculator'),
    ('Gnome Calculator', 'gnome-calculator'),
    ('Qalculate-Gtk', 'qalculate-gtk'),
    ('Qalculate-Qt', 'qalculate-qt'),
]))
PART_ROWS = apps_tail(pkgs([
    ('Kde Partition Manager', 'partitionmanager'),
    ('Gnome Disks Utility', 'gnome-disk-utility'),
    ('Gparted', 'gparted'),
]))
SHOT_ROWS = apps_tail(pkgs([
    ('Flameshot', 'flameshot'),
    ('Kazam', 'kazam'),
    ('Ksnip', 'ksnip'),
    ('Shutter', 'shutter'),
    ('Spectacle', 'spectacle'),
    ('Xfce4-screenshooter', 'xfce4-screenshooter'),
]))
RES_ROWS = apps_tail(pkgs([
    ('Arandr(gui x11)', 'arandr'),
    ('nwg-displays(hyprland-sway-nwg-shell only)', 'nwg-displays'),
    ('wdisplays(gui wayland)', 'wdisplays'),
    ('wlr-randr(cli wayland)', 'wlr-randr'),
    ('xorg-xrandr(cli x11)', 'xorg-xrandr'),
]))
TOOLS_MENU = apps_tail(menu_rows([
    ('App Launchers', 'menu app_launchers'),
    ('Calculators', 'menu calculators'),
    ('Partition tools', 'menu partition_tools'),
    ('Screen Shooters', 'menu screen_shooters'),
    ('Screen Resolution Setters', 'menu screen_resolution'),
]))

SCRIPTS = [
    ('add-repos/upd_servers.sh', 'Main → 1 → 1 Refresh Mirrors'),
    ('add-repos/append_archboki_repo.sh', 'Main → 1 → 3 Add arch-boki Repos'),
    ('add-repos/get-the-arcolinux-keys-and-repos.sh', 'Main → 1 → 4 Add erik_dubois_repos'),
    ('add-repos/install_and_append_chaotic_repo_and_keyrings.sh', 'Main → 1 → 5 Add Chaotic_repos'),
    ('add-repos/fix-pacman-databases-and-keys.sh', 'Main → 1 → 6 Fix pacman_db_and_keys'),
    ('choose-desktop/kde-plasma/install-kde-plasma.sh', 'Main → 2 → 1 Kde - Plasma'),
    ('choose-desktop/xfce/install-xfce-and-sddm.sh', 'Main → 2 → 2 Xfce'),
    ('choose-desktop/cinnamon/install_cinnamon.sh', 'Main → 2 → 3 Cinnamon'),
    ('choose-desktop/hyprland-scripts/00-hyprland-new.sh', 'Main → 2 → 4 Hyprland'),
    ('core-utils/microcode.sh', 'Main → 3 → 1 Microcode'),
    ('core-utils/gpu-drivers.sh', 'Main → 3 → 2 GPU Drivers'),
    ('core-utils/audio-drivers.sh', 'Main → 3 → 3 Audio Drivers'),
    ('install-scripts/123-bluetooth.sh', 'Main → 3 → 4 Bluetooth'),
    ('install-scripts/126-network.sh', 'Main → 3 → 5 Network'),
    ('install-scripts/124-printers.sh', 'Main → 3 → 6 Printers'),
    ('install-scripts/125-installfont-new.sh', 'Main → 3 → 7 Fonts'),
    ('install-scripts/118-core.sh', 'Main → 3 → 8 Core Utils'),
    ('install-scripts/130-archboki-install-apps.sh', 'Main → 4 Install Apps'),
]
INLINE = [
    row('Install gum before the first menu', 'sudo pacman -S gum --needed --noconfirm', 'action',
        'Runs once, before the banner. Not a menu choice.', 'inline'),
    row('Update System', 'sudo pacman -Syyu', 'action', 'Main → 1 → 2. Lives inside 03.', 'inline'),
    row('Install archlinux-tweak-tool-git', 'sudo pacman -S archlinux-tweak-tool-git', 'action',
        'Main → 1 → 7. Lives inside 03. No --needed and no --noconfirm.', 'inline'),
]


def count_rows(section):
    return len(section['rows']) + sum(count_rows(c) for c in section['children'])


def walk_rows(section):
    yield from section['rows']
    for child in section['children']:
        yield from walk_rows(child)


# -------------------------------------------------------------- diagrams
ICON_PATHS = {
    'menu': '<rect x="2" y="2" width="12" height="12" rx="2"/><path d="M5 6.5h6M5 9.5h6M5 12.5h3.5"/>',
    'folder': '<path d="M1.6 5.2h4.4l1.5 1.6h7v6.8h-12.9z"/>',
    'script': '<rect x="2" y="2.5" width="12" height="11" rx="2"/><path d="M5 7.1 7.3 9.2 5 11.3M8.7 11.3h2.8"/>',
}
MARKS = [('menu', 'Menu'), ('folder', 'Submenu'), ('script', 'Action')]


def icon_svg(mark, x, y, color):
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" '
            f'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICON_PATHS[mark]}</g>')


def html_icon(mark):
    return (f'<svg class="glyph" viewBox="0 0 16 16" aria-hidden="true" fill="none" '
            f'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICON_PATHS[mark]}</svg>')


def row_mark(item):
    return 'folder' if item['kind'] == 'menu' else 'script'


def box(x, y, w, h, name, sub=None, kind='menu', mark='menu'):
    """kind is the box (root, menu, leaf). mark is the glyph (menu, folder, script)."""
    out = []
    if kind == 'root':
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{mm.C["paper"]}"/>')
        fill, stroke, sw, dash = mm.C['tint'], mm.C['accent'], 1, ''
        ink = mm.C['accent']
    elif kind == 'leaf':
        fill, stroke, sw, dash = mm.C['leaf'], mm.C['muted'], 0.8, ''
        ink = mm.C['ink']
    else:
        fill, stroke, sw, dash = mm.C['node'], mm.C['ink'], 1, ''
        ink = mm.C['ink']
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="{sw}"{dash}/>')
    out.append(icon_svg(mark, x + 8, y + 8, ink))
    cx = x + w // 2
    if sub:
        out.append(mm.text(cx, y + h - 18, name, 12, mm.C['ink'], mm.SANS, 600))
        out.append(mm.text(cx, y + h - 5, sub, 9, mm.C['soft'], mm.MONO))
    else:
        out.append(mm.text(cx, y + h // 2 + 8, name, 12, mm.C['ink'], mm.SANS, 600))
    return '\n'.join(out)


def legend_marks(y0, note, width):
    out = [f'<line x1="40" y1="{y0}" x2="{width - 40}" y2="{y0}" '
           f'stroke="{mm.C["rule"]}" stroke-width="0.8"/>',
           mm.text(40, y0 + 16, 'LEGEND', 8, mm.C['muted'], mm.MONO, anchor='start',
                   extra=' letter-spacing="0.18em"')]
    x, ky = 40, y0 + 28
    for mark, label in MARKS:
        out.append(icon_svg(mark, x, ky - 3, mm.C['ink']))
        out.append(mm.text(x + 22, ky + 9, label, 8.5, mm.C['muted'], mm.SANS, anchor='start'))
        x += 22 + int(len(label) * 5.2) + 26
    if note:
        out.append(mm.text(x + 8, ky + 9, note, 8.5, mm.C['muted'], mm.SANS, anchor='start',
                           extra=' font-style="italic"'))
    return '\n'.join(out)


def norm_rail(item):
    if isinstance(item, str):
        return item, 'script', 0
    if len(item) == 2:
        return item[0], item[1], 0
    return item


def connect(root_cx, root_bottom, centers, child_y):
    bus = root_bottom + max(12, (child_y - root_bottom) // 2)
    parts = [mm.path(f'M {root_cx} {root_bottom} V {bus}')]
    if len(centers) == 1 and centers[0] == root_cx:
        parts.append(mm.path(f'M {root_cx} {bus} V {child_y}'))
        return parts
    parts.append(mm.path(f'M {centers[0]} {bus} H {centers[-1]}'))
    for cx in centers:
        parts.append(mm.path(f'M {cx} {bus} V {child_y}'))
    return parts


def draw_rail(body, railx, top, rail):
    """Append one indented rail. Returns the y of the last row."""
    step = 26
    if not rail:
        return top
    first = top + 22
    last = first + (len(rail) - 1) * step
    body.append(f'<line x1="{railx}" y1="{top}" x2="{railx}" y2="{last}" '
                f'stroke="{mm.C["rail"]}" stroke-width="0.8"/>')
    for j, item in enumerate(rail):
        label, rmark, indent = norm_rail(item)
        cy = first + j * step
        ix = railx + 14 + indent * 14
        body.append(f'<line x1="{railx}" y1="{cy}" x2="{ix - 2}" y2="{cy}" '
                    f'stroke="{mm.C["rail"]}" stroke-width="0.8"/>')
        body.append(icon_svg(rmark, ix, cy - 11, mm.C['ink']))
        body.append(mm.text(ix + 18, cy + 3, label, 11, mm.C['ink'], mm.SANS, anchor='start'))
    return last


def trunk_svg(slug, title, desc, name, sub, rail, note, mark='menu'):
    """One menu node with the indented rail under it."""
    tw = col_width([(name, sub, 'menu', mark, rail)])
    width = mm.g4(max(tw + 80, 560))
    x0, h = 40, 72
    root_w = min(tw, max(248, int(len(name) * 7.4) + 48))
    root_x = x0 + max(0, (tw - root_w) // 2)
    root_y = 40
    body = [box(root_x, root_y, root_w, h, name, sub, 'menu', mark)]
    last = draw_rail(body, x0 + 16, root_y + h, rail)
    ly = last + 28
    body.append(legend_marks(ly, note, width))
    return fit_svg(mm.svg_wrap(slug, title, desc, width, ly + 56, '\n'.join(body)), width)


def fit_svg(svg, width):
    """Use the drawn width, but allow the picture to shrink by about 15 percent."""
    floor = mm.g4(max(520, width * 0.85))
    old = f'style="min-width:{width}px;max-width:{width}px"'
    new = f'style="width:100%;max-width:{width}px;min-width:{floor}px;height:auto"'
    return svg.replace(old, new, 1)


def col_width(columns):
    need = 248
    for name, sub, _kind, _mark, rail in columns:
        need = max(need, int(len(name) * 7.4) + 48, int(len(sub or '') * 6.2) + 48)
        for item in rail:
            label, _rmark, indent = norm_rail(item)
            need = max(need, 16 + 14 + indent * 14 + 18 + int(len(label) * 6.6) + 20)
    return mm.g4(min(need, 520))


def split_near_half(items):
    """More than four blocks becomes two diagrams, each as close to half as possible."""
    if len(items) <= 4:
        return [items]
    left = (len(items) + 1) // 2
    return split_near_half(items[:left]) + split_near_half(items[left:])


def columns_svg(slug, title, desc, root_name, root_sub, columns, note):
    parts = split_near_half(columns)
    if len(parts) == 1:
        return _columns_svg(slug, title, desc, root_name, root_sub, columns, note)
    drawn = []
    for i, part in enumerate(parts):
        slug_i = slug if i == 0 else f'{slug}-{i + 1}'
        title_i = title if len(parts) == 1 else f'{title} · {i + 1} of {len(parts)}'
        drawn.append(_columns_svg(slug_i, title_i, desc, root_name, root_sub, part, note))
    return '\n'.join(drawn)


def _columns_svg(slug, title, desc, root_name, root_sub, columns, note):
    """columns: (name, sub, kind, mark, rail). rail items are (label, mark) or (label, mark, indent)."""
    n = len(columns)
    tw, gap = col_width(columns), 16
    x0 = 40
    row_w = n * tw + (n - 1) * gap
    width = mm.g4(row_w + 80)
    root_w = 248
    root_x = x0 + (row_w - root_w) // 2
    root_y, tab_y, h = 40, 156, 72
    centers = [x0 + tw // 2 + i * (tw + gap) for i in range(n)]
    body = connect(root_x + root_w // 2, root_y + h, centers, tab_y)
    body.append(box(root_x, root_y, root_w, h, root_name, root_sub, 'root', 'menu'))
    bottom = tab_y + h
    for i, (name, sub, kind, mark, rail) in enumerate(columns):
        tx = x0 + i * (tw + gap)
        body.append(box(tx, tab_y, tw, h, name, sub, kind, mark))
        if not rail:
            continue
        last = draw_rail(body, tx + 16, tab_y + h, rail)
        bottom = max(bottom, last + 16)
    ly = bottom + 28
    body.append(legend_marks(ly, note, width))
    return fit_svg(mm.svg_wrap(slug, title, desc, width, ly + 56, '\n'.join(body)), width)


def script_count(rail):
    return sum(1 for item in rail if norm_rail(item)[1] == 'script')


def branch_columns(groups):
    """A group with more than one choice becomes its own block. The rest sit in Direct actions."""
    direct = []
    columns = []
    for title, children in groups:
        if len(children) > 1:
            n = script_count(children)
            sub = f'{n} action' if n == 1 else f'{n} actions'
            columns.append((title, sub, 'menu', 'folder', children))
        elif len(children) == 1:
            label, mark, _indent = norm_rail(children[0])
            direct.append((label if mark == 'script' else title, 'script'))
        else:
            direct.append((title, 'script'))
    if direct:
        n = len(direct)
        sub = f'{n} action' if n == 1 else f'{n} actions'
        columns.insert(0, ('Direct actions', sub, 'menu', 'folder', direct))
    return columns


def core_svg():
    fonts = [('Regular fonts', 'folder', 0)]
    fonts.extend((name, 'script', 1) for name in REGULAR_FONTS)
    fonts.append(('Nerd fonts', 'folder', 0))
    fonts.extend((name, 'script', 1) for name in NERD_FONTS)
    fonts.append(('Both', 'script', 0))
    columns = branch_columns([
        ('Microcode', []),
        ('GPU drivers', []),
        ('Audio', [('PipeWire', 'script'), ('PulseAudio', 'script')]),
        ('Bluetooth', []),
        ('Network', []),
        ('Printers', []),
        ('Fonts', fonts),
        ('Core utils', []),
    ])
    return columns_svg(
        'core', 'Install Core Utils and Drivers',
        'Core Utils and Drivers. Choices that open another list are their own block. '
        'The rest are Direct actions.',
        'Core Utils and Drivers', 'audio and fonts open more', columns,
        'Direct actions do not open another list. Audio and Fonts do.')


def overview_svg():
    return columns_svg(
        'overview', 'Arch-Boki post-install',
        'Main Menu of 03.arch-boki-post-install-gum.sh. A shell mark is an action. '
        'A folder is a submenu. Quit is only on this menu.',
        '03 Main Menu', 'gum entry',
        [
            ('Update', '7 actions', 'menu', 'folder', [
                ('Refresh mirrors', 'script'), ('Update system', 'script'),
                ('arch-boki repos', 'script'), ('nemesis repo', 'script'),
                ('Chaotic-AUR', 'script'), ('Fix pacman keys', 'script'),
                ('tweak-tool', 'script'),
            ]),
            ('Desktop', '4 installers', 'menu', 'folder', [
                ('Kde - Plasma', 'script'), ('Xfce', 'script'),
                ('Cinnamon', 'script'), ('Hyprland', 'script'),
            ]),
            ('Core utils', 'audio and fonts open more', 'menu', 'folder', [
                ('Microcode', 'script'), ('GPU drivers', 'script'),
                ('Audio', 'folder'),
                ('PipeWire', 'script', 1), ('PulseAudio', 'script', 1),
                ('Bluetooth', 'script'), ('Network', 'script'), ('Printers', 'script'),
                ('Fonts', 'folder'),
                ('Regular fonts', 'script', 1), ('Nerd fonts', 'script', 1),
                ('Both', 'script', 1),
                ('Core utils', 'script'),
            ]),
            ('Install Apps', '8 submenus', 'menu', 'folder', overview_apps_rail()),
            ('Quit', 'exit 0', 'leaf', 'script', []),
        ],
        'Shell mark runs something. Folder opens another menu.')


def overview_apps_rail():
    """Next level only: actions when the menu is a list, folders when it opens more menus."""
    groups = [
        ('File managers', [(r['name'], 'script', 1) for r in FILE_ROWS if r['kind'] == 'action']),
        ('Terminals', [(r['name'], 'script', 1) for r in TERM_ROWS if r['kind'] == 'action']),
        ('Text, pdf, office', [
            ('Text editors', 'folder', 1), ('Office', 'folder', 1), ('Markdown', 'folder', 1),
            ('Pdf viewers', 'folder', 1), ('Dev tools', 'folder', 1),
        ]),
        ('Internet', [
            ('Communication', 'folder', 1), ('Browsers', 'folder', 1),
            ('Downloaders', 'folder', 1), ('Recorders', 'folder', 1),
        ]),
        ('Multimedia', [
            ('Audio players', 'folder', 1), ('Video players', 'folder', 1),
            ('Audio editors', 'folder', 1), ('Video editors', 'folder', 1),
            ('Subtitles', 'folder', 1),
        ]),
        ('Graphics', [
            ('Viewers', 'folder', 1), ('Editors', 'folder', 1), ('Wallpapers', 'folder', 1),
        ]),
        ('System info', [(r['name'], 'script', 1) for r in INFO_ROWS if r['kind'] == 'action']),
        ('System tools', [
            ('Launchers', 'folder', 1), ('Calculators', 'folder', 1), ('Partitions', 'folder', 1),
            ('Screenshots', 'folder', 1), ('Resolution', 'folder', 1),
        ]),
    ]
    rail = []
    for name, kids in groups:
        rail.append((name, 'folder', 0))
        rail.extend(kids)
    return rail


def update_svg():
    rail = [(r['name'], 'script') for r in UPDATE_ROWS if r['kind'] == 'action']
    return trunk_svg(
        'update', 'Update and Refresh',
        'Update and Refresh. Every choice is an action. None of them opens another menu.',
        'Update and Refresh', '7 actions', rail,
        'Each row runs a script or a pacman command, then this menu shows again.')


def desktop_svg():
    rail = [(r['name'], 'script') for r in DESKTOP_ROWS if r['kind'] == 'action']
    return trunk_svg(
        'desktop', 'Choose Desktop',
        'Choose Desktop. Each install waits for Enter, then this menu shows again.',
        'Choose Desktop', '4 installers', rail,
        'Hyprland installs with yay and does not enable a display manager.')


def scripts_svg():
    grouped = []
    seen = []
    for path, _reached in SCRIPTS:
        folder, _, rest = path.partition('/')
        if folder not in seen:
            seen.append(folder)
            grouped.append((folder, []))
        grouped[-1][1].append((rest or path, 'script'))
    grouped.append(('Inside 03', [(item['name'], 'script') for item in INLINE]))
    columns = branch_columns(grouped)
    return columns_svg(
        'scripts', 'Scripts on the path',
        'Scripts 03 calls. A folder with more than one script is its own block. '
        'A single script would sit in Direct actions.',
        'Scripts 03 calls', f'{len(SCRIPTS)} scripts', columns,
        '130 does not call any other script. Anything else in the repo is unused by this menu.')


def section_rail(section):
    """Indented rail: a folder, then the actions under it, same shape as Core Utils."""
    if section.get('children'):
        rail = []
        for child in section['children']:
            if child['label'] == 'Menu':
                continue
            rail.append((child['label'], 'folder', 0))
            for item in child['rows']:
                if item['kind'] in ('action', 'pick'):
                    rail.append((item['name'], 'script', 1))
            for grandchild in child['children']:
                rail.append((grandchild['label'], 'folder', 1))
                for item in grandchild['rows']:
                    if item['kind'] in ('action', 'pick'):
                        rail.append((item['name'], 'script', 2))
        return rail
    return [(item['name'], 'script', 0) for item in section['rows'] if item['kind'] in ('action', 'pick')]


def apps_group_svg(slug, title, sections):
    columns = []
    for section in sections:
        rail = section_rail(section)
        n = sum(1 for item in rail if norm_rail(item)[1] == 'script')
        columns.append((section['label'], f'{n} actions', 'menu', 'folder', rail))
    return columns_svg(
        slug, title,
        f'{title}. Four Install Apps menus. A folder opens the next menu. '
        'A shell mark is one install, indented under that folder when the menu has another level.',
        'Install Apps', title, columns,
        'Same indented tree as Core Utils. Lists under the diagram are these four menus.')


# ---------------------------------------------------------------- html
class Ids:
    def __init__(self):
        self.n = 0
        self.recs = []

    def add(self, item, tab, slug, crumb):
        self.n += 1
        flags = item['kind']
        if item.get('tool'):
            flags += ' ' + item['tool']
        script = item['target']
        if item.get('detail'):
            script += ' ' + item['detail']
        self.recs.append({
            'id': self.n, 'tab': tab, 'slug': slug, 'crumb': crumb,
            'name': item['name'], 'script': script, 'flags': flags,
        })
        return self.n


def chips(item):
    parts = [f'<span class="chip" title="{esc(KIND_TITLE[item["kind"]])}">{esc(item["kind"])}</span>']
    if item.get('tool'):
        parts.append(
            f'<span class="chip alt" title="{esc(TOOL_TITLE[item["tool"]])}">{esc(item["tool"])}</span>')
    detail = item.get('detail')
    if detail:
        parts.append(f'<span class="detail">{esc(detail)}</span>')
    return ''.join(parts)


def rows_html(items, ids, tab, slug, crumb):
    lis = []
    for item in items:
        n = ids.add(item, tab, slug, crumb)
        lis.append(
            f'<li class="row" id="a-{n}"><span class="nm">{html_icon(row_mark(item))}{esc(item["name"])}</span>'
            f'<code>{esc(item["target"])}</code><span>{chips(item)}</span></li>')
    return f'<ul class="rows">{"".join(lis)}</ul>'


def group_html(sections, ids, tab, slug, crumb):
    built = []
    for section in sections:
        path = crumb + [section['label']]
        note = f'<p class="note">{section["note"]}</p>' if section.get('note') else ''
        if section['children']:
            body = note + group_html(section['children'], ids, tab, slug, path)
            count = count_rows(section)
            mark = 'folder'
        else:
            body = note + rows_html(section['rows'], ids, tab, slug, path)
            count = len(section['rows'])
            mark = 'menu'
        built.append((section['label'], count, body, mark))
    return _pack_group(built)


def _pack_group(items):
    # DOM ids must be unique across the page. Use a function attribute.
    start = _pack_group.seq
    buttons, panels = [], []
    for i, (label, count, body, mark) in enumerate(items):
        dom = start + i
        sel = 'true' if i == 0 else 'false'
        buttons.append(
            f'<button type="button" class="subtab" role="tab" id="st-{dom}" aria-controls="sp-{dom}" '
            f'aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{html_icon(mark)}{esc(label)}'
            f'<span class="n">{count}</span></button>')
        panels.append(
            f'<div class="subpanel" role="tabpanel" id="sp-{dom}" aria-labelledby="st-{dom}">'
            f'<h3 class="sub">{html_icon(mark)}{esc(label)} · {count}</h3>{body}</div>')
    _pack_group.seq = start + len(items)
    return (f'<div class="subgroup"><div class="subtabs" role="tablist">{"".join(buttons)}</div>'
            f'{"".join(panels)}</div>')


_pack_group.seq = 1


def diagram_tabs(groups, ids, tab, slug):
    """One subtab per diagram. The diagram is the indented tree; the lists sit under it."""
    built = []
    for label, diagram_slug, sections in groups:
        svg = apps_group_svg(diagram_slug, label, sections)
        lists = tree_html(sections, ids, tab, slug, 'Packages and scripts for the four menus in the diagram.')
        body = f'<div class="diagram-container">\n{svg}\n</div>\n{lists}'
        count = sum(count_rows(s) for s in sections)
        built.append((label, count, body, 'folder'))
    return _pack_group(built)


def tree_html(sections, ids, tab, slug, blurb):
    body = group_html(sections, ids, tab, slug, [])
    return (f'<section class="tree">\n<p class="note">{blurb}</p>\n'
            f'<div class="toolbar"><button type="button" data-act="showall">Show all</button></div>\n'
            f'{body}\n</section>')


def flat_html(items, ids, tab, slug, blurb):
    body = rows_html(items, ids, tab, slug, [])
    return f'<section class="tree">\n<p class="note">{blurb}</p>\n{body}\n</section>'


def howto():
    flags = ''.join(
        f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in {**KIND_TITLE, **TOOL_TITLE}.items())
    return f"""<section class="howto">
<h2>How a choice moves</h2>
<p class="note">Before the first menu, the script runs <code>sudo pacman -S gum --needed --noconfirm</code>, clears the screen, and prints the ARCH BOKI banner. Then it loops the Main Menu. Run it from the repo root. Every action uses a path like <code>./add-repos/...</code>.</p>
<ol>
<li><strong>Menu.</strong> Clears the screen and opens the next menu. It stays on that menu.</li>
<li><strong>Action.</strong> Runs a script or a pacman / yay command, waits for Enter, then shows the same menu again. Apps rows are the exception: there is no Enter pause, and the same submenu stays open.</li>
<li><strong>4. Install Apps</strong> runs <code>install-scripts/130-archboki-install-apps.sh</code> and then exits 03 with that script's status. You do not return to the Main Menu from it.</li>
<li><strong>5. Quit</strong> is only on the Main Menu. It runs <code>exit 0</code>. Back and Main Menu are not listed on the other menus.</li>
</ol>
<p class="note">Only three places open a further menu: the four Main Menu branches, the audio prompt, the font manager, and the apps script. <code>01</code>, <code>02</code>, <code>04</code>, and the Python GUI are earlier tries and are not in this map.</p>
<h3 class="sub">Chips</h3>
<dl class="flags wide">{flags}</dl>
<p class="links"><a class="btn primary" href="{SRC}" target="_blank" rel="noopener">Post-install repo</a>
<a class="btn" href="{MAP_MD}">Source notes</a>
<a class="btn" href="../linutil-menu-map/index.html" target="_blank" rel="noopener">Linutil map</a></p>
</section>"""


def page(panels, ids):
    buttons, sections = [], []
    for i, (slug, label, count, lede, svg, extra) in enumerate(panels):
        is_def = slug == 'overview'
        sel = 'true' if is_def else 'false'
        n = f'<span class="n">{count}</span>' if count else ''
        buttons.append(
            f'<button class="tab" role="tab" id="tab-{slug}" aria-controls="panel-{slug}" '
            f'aria-selected="{sel}" tabindex="{0 if is_def else -1}"'
            f'{" data-default" if is_def else ""}>{esc(label)}{n}</button>')
        diagram = f'<div class="diagram-container">\n{svg}\n</div>' if svg else ''
        sections.append(
            f'<section class="panel" role="tabpanel" id="panel-{slug}" aria-labelledby="tab-{slug}">\n'
            f'<p class="lede">{lede}</p>\n{diagram}\n{extra}\n</section>')
    data = json.dumps(ids.recs, ensure_ascii=False).replace('</', '<\\/')
    css = mm.CSS_BASE + mm.CSS_TABS + _tree_css() + EXTRA_CSS
    early = ("<script>try{var t=localStorage.getItem('linutil-map-theme');"
             "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}"
             "catch(e){}</script>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Arch-Boki post-install map</title>
  {early}
  {mm.FONTS}
  <style>{css}</style>
</head>
<body>
  <div class="frame">
    <div class="topbar"><div>
    <p class="eyebrow">Menu map · Gum</p>
    <h1>Arch-Boki post-install</h1></div>
    <div class="topactions"><a class="btn" href="../index.html">Home</a><a class="btn" href="../linutil-menu-map/index.html" target="_blank" rel="noopener">Linutil map</a><a class="btn" href="{SRC}" target="_blank" rel="noopener">Source repo</a><button type="button" class="themebtn" id="themebtn" aria-pressed="false">Dark mode</button></div></div>
    <p class="lede">Every menu opened by <code>03.arch-boki-post-install-gum.sh</code>, with the script or packages behind each choice. Quit is listed only on the Main Menu.</p>
    <div class="search">
<label for="q">Find a choice</label>
<input id="q" type="search" placeholder="name, package or script, e.g. pipewire, nemo, chaotic" autocomplete="off">
<p class="count" id="qc" aria-live="polite"></p>
<ul class="results" id="qr"></ul>
</div>
    <div class="tabs" role="tablist" aria-label="Arch-Boki post-install menus">
      {''.join(buttons)}
    </div>
    {''.join(sections)}
  </div>
  <script type="application/json" id="entries">{data}</script>
  <script>{JS}</script>
</body>
</html>
"""


def _tree_css():
    spec_tree = importlib.util.spec_from_file_location(
        'tree', ROOT / 'linutil-menu-map-generator' / 'gen_menu_tree.py')
    tree = importlib.util.module_from_spec(spec_tree)
    spec_tree.loader.exec_module(tree)
    return tree.CSS_TREE


def check():
    assert len(REGULAR_FONTS) == 33, len(REGULAR_FONTS)
    assert len(NERD_FONTS) == 24, len(NERD_FONTS)
    assert len(UPDATE_ROWS) == 7
    assert len(DESKTOP_ROWS) == 4
    assert len(CORE_MENU) == 8
    assert len(MAIN_ROWS) == 5
    assert len(FILE_ROWS) == 8
    assert len(TERM_ROWS) == 6
    assert len(EDITOR_ROWS) == 6
    assert len(INFO_ROWS) == 14
    assert len(WALL_ROWS) == 9
    assert len(LAUNCH_ROWS) == 9
    assert len(SCRIPTS) == 18
    assert sum(1 for r in FILE_ROWS if r['kind'] == 'action') == 8
    assert sum(1 for r in APLAYER_ROWS if r['kind'] == 'action') == 11


def main():
    check()
    ids = Ids()
    font_note = ('On a pick list: numbers separated by spaces (for example 1 3 5), '
                 'a or all for every font, b to go back, q to quit the font script. '
                 'After an install it asks for Enter, or q to quit. wget and unzip are '
                 'installed first if they are missing. That check runs on the Nerd Font path.')
    apps_note = ('Every install line is sudo pacman -S --needed --noconfirm unless the row says yay. '
                 'There is no Enter pause.')
    panels = [
        ('overview', 'Overview', '',
         'The gum entry point. Choice 5 is Quit. The other four choices open a menu.',
         overview_svg(),
         flat_html(MAIN_ROWS, ids, 'Main Menu', 'overview',
                   'Quit is listed only here.')),
        ('update', 'Update', '7',
         'Menu title on screen: Update and Refresh. No choice here opens another menu.',
         update_svg(),
         flat_html(UPDATE_ROWS, ids, 'Update', 'update',
                   'Refresh, update, repos, keys, and the tweak tool.')),
        ('desktop', 'Desktop', '4',
         'Menu title on screen: Choose Desktop. Each install waits for Enter, then this menu shows again.',
         desktop_svg(),
         flat_html(DESKTOP_ROWS, ids, 'Desktop', 'desktop',
                   'No choice here opens another menu. Hyprland installs with yay and does not enable a display manager.')),
        ('core', 'Core', '',
         'Menu title on screen: Install Core Utils and Drivers. Choices 3 and 7 open another prompt.',
         core_svg(),
         tree_html([
             sec('Menu', CORE_MENU, 'The eight install choices. Audio and Fonts open another prompt.'),
             sec('Audio prompt', AUDIO_ROWS,
                 'On screen: Which audio system would you like to install? 1 PipeWire, 2 PulseAudio.'),
             sec('Font manager', FONT_MENU, font_note),
             sec('Regular fonts', REGULAR_ROWS,
                 'Installed with sudo pacman -S --needed --noconfirm, then sudo fc-cache -f -v.'),
             sec('Nerd fonts', NERD_ROWS,
                 'Zip name is the file under nerd-fonts release v3.4.0. A directory that already has files is skipped.'),
         ], ids, 'Core', 'core',
             'Open a sub-tab for the menu, the audio prompt, or a font list.')),
        ('apps', 'Apps', '',
         '03 prints Installing Apps... and runs install-scripts/130-archboki-install-apps.sh. The eight menus are split into two diagrams of four. 130 does not call any other script.',
         None,
         flat_html(APPS_TOP, ids, 'Apps', 'apps',
                   'The eight categories. The two subtabs below each draw four of them.')
         + diagram_tabs([
             ('Files and web', 'apps-files', [
                 sec('File Managers', FILE_ROWS, apps_note),
                 sec('Terminal Emulators', TERM_ROWS, apps_note),
                 sec('Text, pdf, office', children=[
                     sec('Menu', TEXT_MENU, 'This menu only opens more menus.'),
                     sec('Text Editors', EDITOR_ROWS, apps_note),
                     sec('Office suites', OFFICE_ROWS, apps_note),
                     sec('Markdown Editors', MD_ROWS, apps_note),
                     sec('Pdf Viewers', PDF_ROWS, apps_note),
                     sec('Dev Tools', DEV_ROWS, apps_note),
                 ]),
                 sec('Internet', children=[
                     sec('Menu', NET_MENU, 'This menu only opens more menus. The communication function is spelled comunication.'),
                     sec('Comunication/Social', COMM_ROWS, apps_note),
                     sec('Web Browsers', BROWSER_ROWS, apps_note),
                     sec('Downloaders', DOWN_ROWS, apps_note),
                     sec('Recorders', REC_ROWS, apps_note),
                 ]),
             ]),
             ('Media and tools', 'apps-media', [
                 sec('Multimedia', children=[
                     sec('Menu', MEDIA_MENU, 'This menu only opens more menus.'),
                     sec('Audio Players', APLAYER_ROWS, apps_note),
                     sec('Video Players', VPLAYER_ROWS, apps_note),
                     sec('Audio Editors', AEDIT_ROWS, 'Openshot is on this menu. ' + apps_note),
                     sec('Video Editors', VEDIT_ROWS, apps_note),
                     sec('Subtitle Editors', SUB_ROWS, apps_note),
                 ]),
                 sec('Graphics', children=[
                     sec('Menu', GFX_MENU, 'This menu only opens more menus.'),
                     sec('Photo/Image Viewers', VIEW_ROWS, apps_note),
                     sec('Photo/Image editors', EDIT_ROWS, apps_note),
                     sec('Wallpaper/Backround Changer', WALL_ROWS, apps_note),
                 ]),
                 sec('System Info/Monitoring', INFO_ROWS, apps_note),
                 sec('System Tools', children=[
                     sec('Menu', TOOLS_MENU, 'This menu only opens more menus.'),
                     sec('App Launchers', LAUNCH_ROWS, apps_note),
                     sec('Calculators', CALC_ROWS, apps_note),
                     sec('Partition Tools', PART_ROWS, apps_note),
                     sec('Screen Shooters', SHOT_ROWS, apps_note),
                     sec('Screen Resolution', RES_ROWS, apps_note),
                 ]),
             ]),
         ], ids, 'Apps', 'apps')),
        ('scripts', 'Scripts', '',
         'Eighteen scripts are on the path. Three more rows are commands that live inside 03. Anything else in the post-install repo is unused by this menu.',
         scripts_svg(),
         flat_html(
             [row(path, reached, 'action', None, 'script') for path, reached in SCRIPTS] + INLINE,
             ids, 'Scripts', 'scripts',
             '130 does not call any other script. Font and audio choices stay inside their own file.')),
        ('about', 'About', '',
         'How this map follows the post-install script.',
         None,
         howto()),
    ]
    # Fill counts for tabs that were left blank, from the rows just indexed.
    by_slug = {}
    for rec in ids.recs:
        by_slug[rec['slug']] = by_slug.get(rec['slug'], 0) + 1
    filled = []
    for slug, label, count, lede, svg, extra in panels:
        if not count and slug in by_slug:
            count = str(by_slug[slug])
        filled.append((slug, label, count, lede, svg, extra))
    OUT.write_text(page(filled, ids))
    print(f'wrote {OUT} ({len(ids.recs)} entries)')


if __name__ == '__main__':
    main()
