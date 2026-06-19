"""
Backport of qtile PR #5975 fixes for version 0.36.0.

These patches guard against finalized widgets/bars still receiving hook
callbacks after screen reconfiguration.  Remove this file (and the import
in config.py) once qtile ships a version that includes PR #5975.

Each patch stores the true original function as `_pr5975_original` on the
patched replacement.  On every apply() call (including config reloads), the
true original is retrieved and a fresh patch is installed — no accumulation
of wrapper layers, no stale code surviving across reloads.
"""

from libqtile import bar as _bar
from libqtile.widget import base as _widget_base
from libqtile.widget import currentscreen as _currentscreen


def apply() -> None:
    _patch_widget_length()
    _patch_bar_actual_draw()
    _patch_bar_finalize()
    _patch_currentscreen_update_text()


def _get_original(func, attr: str = "_pr5975_original"):
    """Return the true pre-patch original, unwrapping previous patches."""
    return getattr(func, attr, func)


def _patch_widget_length() -> None:
    orig_fget = _get_original(_widget_base._Widget.length.fget)
    orig_fset = _widget_base._Widget.length.fset

    def length(self, _orig=orig_fget):
        if self.finalized:
            return 0
        return _orig(self)

    length._pr5975_original = orig_fget
    _widget_base._Widget.length = property(length, orig_fset)


def _patch_bar_actual_draw() -> None:
    orig = _get_original(_bar.Bar._actual_draw)

    def _actual_draw(self, _orig=orig):
        self._draw_queued = False
        if not self.window or not hasattr(self, "drawer"):
            return
        _orig(self)

    _actual_draw._pr5975_original = orig
    _bar.Bar._actual_draw = _actual_draw


def _patch_bar_finalize() -> None:
    orig = _get_original(_bar.Bar.finalize)

    def finalize(self, _orig=orig):
        self._draw_queued = False
        _orig(self)

    finalize._pr5975_original = orig
    _bar.Bar.finalize = finalize


def _patch_currentscreen_update_text() -> None:
    orig = _get_original(_currentscreen.CurrentScreen.update_text)

    def update_text(self, _orig=orig):
        if self.layout is None:
            return
        _orig(self)

    update_text._pr5975_original = orig
    _currentscreen.CurrentScreen.update_text = update_text
