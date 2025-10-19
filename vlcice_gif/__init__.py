# VlčiceGIF module for Tockar Discord Bot
# Adapted from pie framework to discord.py
# Source: https://github.com/pumpkin-py/pumpkin-fun/tree/main/fun

from .gif_functions import (
    get_pet_frames,
    get_hyperpet_frames,
    get_bonk_frames,
    get_whip_frames,
    get_spank_frames,
    get_lick_frames,
    get_hyperlick_frames,
)
from .helpers import get_users_avatar, create_transparent_gif

__all__ = [
    'get_pet_frames',
    'get_hyperpet_frames', 
    'get_bonk_frames',
    'get_whip_frames',
    'get_spank_frames',
    'get_lick_frames',
    'get_hyperlick_frames',
    'get_users_avatar',
    'create_transparent_gif',
]