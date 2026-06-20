# qtile config

Personal [qtile](https://qtile.org/) Wayland configuration, used across multiple machines (laptops and desktops).

## Structure

```
~/.config/qtile/
├── config.py               # Main configuration
├── autostart.sh            # Startup hook (shikane, dunst)
├── hosts/
│   ├── __init__.py         # Hostname dispatcher — exposes `cfg`
│   ├── default.py          # Baseline defaults (desktop: no battery/wlan/brightness)
│   └── <hostname>.py       # Per-machine overrides
└── backgrounds/            # Wallpapers
```

## Multi-machine support

At startup, `hosts/__init__.py` detects the current hostname and imports the matching module as `cfg`. If no host-specific file exists, it falls back to `hosts/default.py` and logs a warning.

Each host file defines three feature flags:

| Flag | Effect when `True` |
|------|--------------------|
| `has_battery` | Battery widget shown in bar |
| `has_wlan` | WiFi widget shown in bar |
| `has_brightness` | `XF86MonBrightness` keys bound |

`default.py` sets all three to `False` (safe desktop baseline).

### Adding a new machine

1. Get the normalized hostname:
   ```sh
   python3 -c "import socket; print(socket.gethostname().replace('.','_').replace('-','_'))"
   ```
2. Create `hosts/<that_name>.py`:
   ```python
   from hosts.default import *

   has_battery = True   # set as appropriate
   has_wlan = True
   has_brightness = True
   ```
3. Reload the config (`mod+ctrl+r`). No other files need to change.

## Screen management

Qtile is configured with a pool of 8 pre-built `Screen` objects. With `reconfigure_screens = True`, qtile's Wayland backend activates exactly as many as there are connected outputs — the rest are unused. This means screen count is fully dynamic: docking and undocking work without any config changes.

Display layout (resolution, position, refresh rate) is handled separately by **shikane** (`~/.config/shikane/config.toml`), which matches monitors by serial number and applies the right profile automatically.

### Shikane profiles

| Profile | Monitors |
|---------|----------|
| `laptop builtin` | Built-in display only (eDP-1) |
| `office` | 3× Dell S2721QSA 4K + Samsung 2880×1800 |
| `Home Office` | Dell U2723QE 4K + Philips 276E8V 4K + Samsung 2880×1800 |
| `aixigo Office` | 3× Dell S2721QSA 4K + Samsung 2880×1800 |

## Keybindings

`mod` is the Super key. Navigation keys follow the [NEO layout](https://neo-layout.org/) (`s/n/k/t` in place of `h/j/k/l`).

| Key | Action |
|-----|--------|
| `mod+s/t` | Focus left/right |
| `mod+n/k` | Focus down/up |
| `mod+Return` | Launch terminal |
| `mod+a` | Rofi launcher |
| `mod+x` | Kill window |
| `mod+e` | Toggle fullscreen |
| `mod+shift+space` | Toggle floating |
| `mod+Tab` | Next layout |
| `mod+ctrl+r` | Reload config |
| `mod+ctrl+q` | Quit qtile |
| `mod+i` | Show window info (notify) |
| `Scroll_Lock` → `Pause` | Lock screen (swaylock) |
| `F12` | Toggle scratchpad terminal |

## Autostart

`autostart.sh` runs once on startup:
- **shikane** — Wayland output management
- **dunst** — notification daemon
