# qtile config

Personal [qtile](https://qtile.org) configuration running on Wayland. Based on the default config, extended for a multi-monitor, multi-machine laptop/desktop setup.

## Structure

```
~/.config/qtile/
  config.py                  main configuration
  autostart.sh               startup script (shikane, dunst)
  hosts/
    __init__.py              hostname detection and host config import
    default.py               fallback host config (desktop without extras)
    <hostname>.py            per-machine overrides
  backgrounds/
    green-galaxy.jpg         wallpaper
~/.config/shikane/
  configs/
    <hostname>.toml          per-machine monitor layout profiles
```

## Multi-machine setup

Host-specific settings live in `hosts/<hostname>.py` (dots and dashes in the hostname are replaced with underscores). The file only needs to override what differs from the defaults:

```python
# hosts/default.py
has_battery: bool = False
has_wlan: bool = False
has_brightness: bool = False
```

| Flag | Effect |
|---|---|
| `has_battery` | Shows battery widget in the bar |
| `has_wlan` | Shows WLAN and network widgets in the bar |
| `has_brightness` | Enables `XF86MonBrightness` keybindings |

Adding a new machine: create `hosts/<hostname>.py` and, if needed, `~/.config/shikane/configs/<hostname>.toml`.

## Monitor layout

[shikane](https://github.com/moritzkoerber/shikane) manages output configuration. `autostart.sh` selects the per-host shikane config via `shikane -c ~/.config/shikane/configs/$(hostname).toml`, falling back to the default `~/.config/shikane/config.toml` if no host-specific file exists.

Screen objects are created dynamically via `generate_screens`, sorted left-to-right by physical position. The leftmost screen gets the primary bar (with Prompt, Chord, StatusNotifier). Screen objects are cached by output port name so that shikane's output reconfiguration events don't cause bar re-initialization.

## Keyboard layout

Neo2 (`de` / `neo` variant). The movement keys are remapped accordingly:

| Direction | Neo2 key |
|---|---|
| left | S |
| right | T |
| down | N |
| up | K |

## Keybindings

`mod` is the Super key.

### Windows and focus

| Key | Action |
|---|---|
| `mod + S/T/N/K` | Move focus left/right/down/up |
| `mod + Space` | Move focus to next window |
| `mod + Shift + S/T/N/K` | Move window left/right/down/up |
| `mod + Ctrl + S/T/N/K` | Grow window left/right/down/up |
| `mod + B` | Reset window sizes |
| `mod + X` | Kill focused window |
| `mod + E` | Toggle fullscreen |
| `mod + Shift + Space` | Toggle floating |
| `mod + Shift + Return` | Toggle split/unsplit stack |

### Layouts and groups

| Key | Action |
|---|---|
| `mod + Tab` | Next layout |
| `mod + 1–9` | Switch to group |
| `mod + Shift + 1–9` | Move window to group (and follow) |
| `mod + Ctrl + 1–9` | Move window to group (stay) |

### Scratchpad

| Key | Action |
|---|---|
| `F12` | Toggle scratchpad terminal (alacritty) |

### Applications and system

| Key | Action |
|---|---|
| `mod + Return` | Launch terminal |
| `mod + A` | Launch rofi app launcher |
| `mod + I` | Show info notification for focused window |
| `mod + Ctrl + R` | Reload config |
| `mod + Ctrl + Q` | Shutdown qtile |
| `Scroll_Lock → Pause` | Lock screen (swaylock, random colour) |

### Media

| Key | Action |
|---|---|
| `XF86AudioPlay` | Play/pause (mpc) |
| `XF86AudioNext/Prev/Stop` | Next/previous/stop (mpc) |
| `XF86AudioMute` | Toggle mute (wpctl) |
| `XF86AudioRaiseVolume` | Volume +3% (wpctl) |
| `XF86AudioLowerVolume` | Volume −3% (wpctl) |
| `XF86MonBrightnessUp/Down` | Brightness ±10% (brightnessctl) — laptop only |

### Virtual terminals (Wayland)

| Key | Action |
|---|---|
| `Ctrl + Alt + F1–F7` | Switch VT |

## Layouts

| Layout | Description |
|---|---|
| Columns | Default, up to 3 columns, new windows insert to the right |
| Max | Single maximised window |
| TreeTab | Tabbed tree view |

## Bar

Each screen has a bar (24 px). The primary screen bar includes extra widgets: Prompt, Chord indicator, and StatusNotifier (system tray).

**All screens:**
CurrentLayout · GroupBox · CurrentScreen · TaskList · Mpd2 · CPU graph · CPU · Memory graph · Memory · *(wlan/net if applicable)* · *(battery if applicable)* · Volume · Clock

**Primary screen only (appended):**
StatusNotifier

## Floating windows

The following windows open floating by default:

- Standard dialog types (`wm_type="dialog"`, transient windows)
- `"Open Files"` dialogs (e.g. Teams file picker)
- gitk dialogs, ssh-askpass, pinentry

Use `mod + I` to inspect an unfloating dialog and identify its `name` or `wm_class` for adding a new rule.

## Dependencies

| Tool | Purpose |
|---|---|
| [shikane](https://github.com/moritzkoerber/shikane) | Monitor layout profiles |
| [dunst](https://dunst-project.org) | Notification daemon |
| [swaylock](https://github.com/swaywm/swaylock) | Screen locker |
| [rofi](https://github.com/davatorium/rofi) | App launcher |
| [alacritty](https://alacritty.org) | Terminal (scratchpad) |
| [mpc](https://www.musicpd.org/clients/mpc/) / [mopidy](https://mopidy.com) | Music playback |
| [wpctl](https://pipewire.org) | Audio control (PipeWire) |
| [brightnessctl](https://github.com/Hummer12007/brightnessctl) | Backlight control (laptops) |

## Known workarounds

**qtile PR #5975** — not yet in the installed version (0.36.0). `_finalize_configurables()` finalizes widgets before bars, causing queued `Bar._actual_draw()` calls to run against widgets with `drawer.ctx = None`. The config monkey-patches `_Widget.length` (returns 0 when finalized) and `Bar._actual_draw` (exits early when the window is gone). Remove the patch block in `config.py` once qtile ships this fix.
