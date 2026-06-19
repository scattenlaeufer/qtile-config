"""
My personal qtile configuration. The default config was used as a start and
then extended to meet my personal meets.
"""

# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import logging
import random
import subprocess
from pathlib import Path

from libqtile import bar, hook, layout, qtile, widget
from libqtile.backend.wayland import InputConfig
from libqtile.config import (
    Click,
    Drag,
    Group,
    Key,
    KeyChord,
    Match,
    Output,
    Screen,
    ScratchPad,
    DropDown,
)
from libqtile.lazy import lazy
from libqtile.log_utils import logger
from libqtile.utils import guess_terminal

# from qtile_bonsai import Bonsai

from hosts import cfg
import qtile_fixes; qtile_fixes.apply()

log = logging.getLogger(__name__)

mod = "mod4"
terminal = guess_terminal()

rofi_cmd = "rofi -show drun"


def lock_cmd():
    r = lambda: random.randint(0, 50)
    return f"swaylock --color {r():02x}{r():02x}{r():02x} --show-failed-attempts"


@lazy.function
def run_screenlock(qtile):
    cmd = lock_cmd()
    qtile.spawn(cmd)


@hook.subscribe.startup_once
def autostart() -> None:
    subprocess.call(str(Path("~/.config/qtile/autostart.sh").expanduser()))

    # Advertise the Wayland session to systemd and D-Bus so that logind
    # recognises qtile as the active compositor and doesn't reclaim the
    # DRM device on monitor hotplug.
    env_vars = ["WAYLAND_DISPLAY", "XDG_CURRENT_DESKTOP", "DISPLAY"]
    subprocess.Popen(
        ["systemctl", "--user", "import-environment"] + env_vars
    ).wait()
    subprocess.Popen(
        ["dbus-update-activation-environment", "--systemd"] + env_vars
    ).wait()


@lazy.function
def notify_window_info(qtile) -> None:
    w = qtile.current_window
    if not w:
        return
    i = w.info()
    msg = "\n".join(
        [
            f"name:      {i.get('name')}",
            f"wm_class:  {i.get('wm_class')}",
            f"wm_type:   {i.get('wm_type')}",
            f"shell:     {i.get('shell')}",
            f"floating:  {i.get('floating')}",
            f"position:  {i.get('x')}, {i.get('y')}",
            f"size:      {i.get('width')} x {i.get('height')}",
        ]
    )
    qtile.spawn(f"notify-send 'Window Info' '{msg}'")


@hook.subscribe.suspend
def suspend_lock():
    qtile.spawn(lock_cmd())


neo = {
    "h": "s",
    "j": "n",
    "k": "k",
    "l": "t",
    "s": "i",
    "n": "b",
}

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], neo["h"], lazy.layout.left(), desc="Move focus to left"),
    Key([mod], neo["l"], lazy.layout.right(), desc="Move focus to right"),
    Key([mod], neo["j"], lazy.layout.down(), desc="Move focus down"),
    Key([mod], neo["k"], lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key(
        [mod, "shift"],
        neo["h"],
        lazy.layout.shuffle_left(),
        desc="Move window to the left",
    ),
    Key(
        [mod, "shift"],
        neo["l"],
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([mod, "shift"], neo["j"], lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], neo["k"], lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key(
        [mod, "control"],
        neo["h"],
        lazy.layout.grow_left(),
        desc="Grow window to the left",
    ),
    Key(
        [mod, "control"],
        neo["l"],
        lazy.layout.grow_right(),
        desc="Grow window to the right",
    ),
    Key([mod, "control"], neo["j"], lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], neo["k"], lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], neo["n"], lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "x", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "e",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key(
        [mod, "shift"],
        "space",
        lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window",
    ),
    Key(
        [mod, "control"],
        "r",
        lazy.reload_config(),
        # lazy.spawn(Path("~/.config/polybar/startup.sh")),
        # lazy.spawn("feh --bg-scale ~/.config/i3/green-galaxy.jpg"),
        desc="Reload the config",
    ),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "a", lazy.spawn(rofi_cmd), desc="Spawn rofi to launce a program"),
    Key([mod], "i", notify_window_info(), desc="Show focused window info"),
    KeyChord(
        [],
        "Scroll_Lock",
        [Key([], "Pause", run_screenlock(), desc="Lock screen on key press")],
    ),
    # Key(
    #     [],
    #     "Pause",
    #     run_screenlock(),
    #     desc="Lock screen on key press",
    # ),
    # Multimedia Keys
    Key([], "XF86AudioPlay", lazy.spawn("mpc toggle"), desc="Play/Pause via MPC"),
    Key([], "XF86AudioNext", lazy.spawn("mpc next"), desc="Play next song via MPC"),
    Key([], "XF86AudioPrev", lazy.spawn("mpc prev"), desc="Play prev song via MPC"),
    Key([], "XF86AudioStop", lazy.spawn("mpc stop"), desc="Stop playback via MPC"),
    # Audio Keys
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn("wpctl set-mute @DEFAULT_SINK@ toggle"),
        desc="Toggle audio mute",
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn("wpctl set-volume @DEFAULT_SINK@ .03+"),
        desc="Raise audio volume by 3%",
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn("wpctl set-volume @DEFAULT_SINK@ .03-"),
        desc="Lower audio volume by 3%",
    ),
    # Monitor Brightness
]

if cfg.has_brightness:
    keys += [
        Key(
            [],
            "XF86MonBrightnessDown",
            lazy.spawn("brightnessctl set -q 10%-"),
            desc="Lower monitor birghtness by 10%",
        ),
        Key(
            [],
            "XF86MonBrightnessUp",
            lazy.spawn("brightnessctl set -q 10%+"),
            desc="Raise monitor birghtness by 10%",
        ),
    ]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
            # mod + shift + group number = move focused window to group
            Key(
                [mod, "control"],
                i.name,
                lazy.window.togroup(i.name),
                desc=f"move focused window to group {i.name}",
            ),
        ]
    )

groups.append(
    ScratchPad(
        "scratchpad",
        [DropDown("term", "alacritty --option window.opacity=1", opacity=1)],
    )
)
keys.extend([Key([], "F12", lazy.group["scratchpad"].dropdown_toggle("term"))])

layouts = [
    layout.Columns(
        border_focus_stack=["#0788c9", "#002376"],
        border_focus="#0788c9",
        border_normal="#424261",
        border_width=1,
        insert_position=1,
        num_columns=3,
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    # Bonsai(
    #     **{
    #         "window.border_size": 1,
    #         "tab_bar.height": 20,
    #         "tab_bar.tab.width": "auto",
    #         "tab_bar.tab.title_provider": lambda _index, active_pane, _tab: active_pane.window.name,
    #     }
    # ),
]

widget_defaults = {"font": "DejaVus ans mono", "fontsize": 12, "padding": 3}
extension_defaults = widget_defaults.copy()

bar_height = 24
wallpaper_path = Path("~/.config/qtile/backgrounds/green-galaxy.jpg")


def _build_bar(is_main: bool = False) -> bar.Bar:
    right: list = [
        widget.Sep(),
        widget.CPUGraph(),
        widget.CPU(format="CPU {freq_current:3.1f}GHz {load_percent:5.1f}%"),
        widget.Sep(),
        widget.MemoryGraph(),
        widget.Memory(
            format="Mem: {MemUsed:4.1f}{mm}/{MemTotal:4.1f}{mm} Swap: {SwapUsed:4.1f}{ms}/{SwapTotal:4.1f}{ms}",
            measure_mem="G",
            measure_swap="G",
        ),
        widget.Sep(),
    ]
    if cfg.has_wlan:
        right += [widget.Wlan(format="{essid} {percent:2.0%}"), widget.Net(prefix="M"), widget.Sep()]
    if cfg.has_battery:
        right += [widget.Battery(), widget.Sep()]
    right += [widget.PulseVolume(), widget.Sep(), widget.Clock(format="KW%W %Y-%m-%d %a %H:%M:%S")]

    left: list = [
        widget.CurrentLayout(mode="icon"),
        widget.Sep(),
        widget.GroupBox(disable_drag=True),
        widget.Sep(),
        widget.CurrentScreen(),
        widget.Sep(),
    ]

    if is_main:
        middle: list = [
            widget.Prompt(),
            widget.TaskList(),
            widget.Chord(
                chords_colors={"launch": ("#ff0000", "#ffffff")},
                name_transform=lambda name: name.upper(),
            ),
            widget.Mpd2(idle_message="mopidy idle"),
        ]
        widgets = left + middle + right + [widget.Sep(), widget.StatusNotifier()]
    else:
        middle = [widget.TaskList(), widget.Mpd2(idle_message="mopidy idle")]
        widgets = left + middle + right

    return bar.Bar(
        widgets,
        bar_height,
        # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
        # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
    )

_wp = str(wallpaper_path.expanduser())

# Maps port name → (Screen, (x, y, width, height)).
# Cleared per-entry when the output geometry changes so wlroots gets a fresh
# internal window/surface after dock events where a screen moves position.
_screen_cache: dict[str, tuple[Screen, tuple[int, int, int, int]]] = {}


def generate_screens(outputs: list[Output]) -> list[Screen]:
    active_ports = {o.port for o in outputs}

    for port in list(_screen_cache.keys()):
        if port not in active_ports:
            del _screen_cache[port]

    # Determine which port gets the main bar (leftmost by position)
    main_port = min(outputs, key=lambda o: (o.rect.x, o.rect.y)).port if outputs else None

    result: list[Screen] = []
    for output in outputs:
        port = output.port
        geom = (output.rect.x, output.rect.y, output.rect.width, output.rect.height)

        if port in _screen_cache and _screen_cache[port][1] != geom:
            del _screen_cache[port]

        if port not in _screen_cache:
            _screen_cache[port] = (
                Screen(
                    top=_build_bar(is_main=(port == main_port)),
                    wallpaper=_wp,
                    wallpaper_mode="fill",
                ),
                geom,
            )
        result.append(_screen_cache[port][0])
    return result

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_type="dialog"),
        Match(func=lambda c: bool(c.is_transient_for())),
        Match(title="Open Files"),
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = {"type:keyboard": InputConfig(kb_layout="de", kb_variant="neo")}

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
