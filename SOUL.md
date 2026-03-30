# SOUL — System Overview & User Layout

## Hardware
- CPU: AMD Ryzen 5 3400G (4C/8T, 3.7GHz)
- GPU: AMD Radeon RX 6600 8GB (Navi 23, gfx1032, ROCm via HSA_OVERRIDE_GFX_VERSION=10.3.0)
- RAM: 16GB DDR4
- Storage: NVMe SSD
- PCIe: Gen 3.0

## OS
- Arch Linux (CachyOS kernel)
- Compositor: Hyprland (Wayland — no X11, no xdotool)
- Shell: zsh
- Terminal: kitty
- Browser: Brave
- File Manager: Thunar
- Audio: PipeWire + WirePlumber

## Hyprland Keybinds
- Super+Q: close active window
- Super+T: open kitty terminal
- Super+E: open thunar
- Super+B: open brave
- Super+Space: rofi launcher
- Ctrl+Space: wallpaper picker (waypaper)
- Super+1-9: switch workspace

## Package Management
- System packages: `sudo pacman -S --noconfirm <pkg>`
- AUR packages: `yay -S --noconfirm <pkg>`
- Python packages: `pip install <pkg>` or `uv pip install <pkg>`
- Search: `pacman -Ss <query>` / `yay -Ss <query>`

## Common App Binary Names
| App | Binary | Launch |
|-----|--------|--------|
| Firefox | firefox | `firefox &` |
| Brave | brave | `brave &` |
| Thunar | thunar | `thunar &` |
| Kitty | kitty | `kitty &` |
| VS Code | code | `code &` |
| Discord | discord | `discord &` |
| Spotify | spotify | `spotify &` |
| mpv | mpv | `mpv <file/url> &` |

## Media Operations
- Play audio/video: `mpv --no-video ytdl://ytsearch:"query" &`
- Play video: `mpv ytdl://ytsearch:"query" &`
- Download video: `yt-dlp "URL" -f "best[height<=1080]" -o "~/Downloads/%(title)s.%(ext)s"`
- Stop media: `pkill mpv`

## System Operations
- Volume up: `pactl set-sink-volume @DEFAULT_SINK@ +10%`
- Volume down: `pactl set-sink-volume @DEFAULT_SINK@ -10%`
- Set volume: `pactl set-sink-volume @DEFAULT_SINK@ 50%`
- Mute toggle: `pactl set-sink-mute @DEFAULT_SINK@ toggle`
- Brightness: `brightnessctl set 50%`
- Screenshot: `grim ~/Pictures/screenshot_$(date +%s).png`
- Screenshot region: `grim -g "$(slurp)" ~/Pictures/screenshot_$(date +%s).png`
- Wallpaper: `~/.config/hypr/scripts/theme_matugen/theme_ctl.sh random`
- Lock screen: `hyprlock`
- Reboot: `systemctl reboot`
- Shutdown: `systemctl poweroff`
- Suspend: `systemctl suspend`

## Window Management
- Close specific app: `pkill <appname>` (NOT hyprctl dispatch killactive)
- Close active window: `hyprctl dispatch killactive`
- List open windows: `hyprctl clients -j | jq -r '.[].class'`
- Check if app running: `pgrep -x <binary>`
- Focus window: `hyprctl dispatch focuswindow <class>`

## File Paths
- Home: /home/gamerx
- Downloads: ~/Downloads
- Documents: ~/Documents
- Pictures: ~/Pictures
- Configs: ~/.config
- ARIA: ~/aria

## Connected Devices
- Android phone: via ADB (`adb shell`)
- Phone IP: check with `adb shell ip addr`

## Sudo
- Password available in vault (auto-injected by ARIA router)

## ARIA Modules
- Telegram: active (router.py)
- Voice: active (listener.py + speaker.py)
- Vision: active (capture.py + analyze.py)
- Browser: via Antigravity
- Skills: ~/aria/skills/
- Identity: ~/aria/identity.yaml (purpose-tagged accounts, decision rules)
  - `email_agent.py`: Send and read emails
  - `social_agent.py`: Post to X/Twitter and LinkedIn
  - `research_agent.py`: Search the web and perform market analysis
  - `business_agent.py`: Generate business plans and analyze competitors

## Rules for Antigravity
When performing tasks on this system:
1. Always use the binary names from the table above
2. Background GUI apps with `&`
3. Use `pkill appname` to close specific apps
4. Use `pactl` for volume, not mpv
5. Use `yt-dlp` for downloads, `mpv` for playback
6. Verify actions with `pgrep` or `hyprctl clients`
7. Package install with `pacman` first, `yay` for AUR only
8. NO xdotool — use Hyprland IPC or ydotool for automation
9. Screenshots with `grim` (Wayland-native)
