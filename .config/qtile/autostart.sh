#!/usr/bin/env sh

SHIKANE_CFG="$HOME/.config/shikane/configs/$(hostname).toml"
if [ -f "$SHIKANE_CFG" ]; then
    shikane -c "$SHIKANE_CFG" &
else
    shikane &
fi
dunst &
