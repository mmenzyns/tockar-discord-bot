"""
GIF Generation Functions from vlcice_gif module
Extracted and simplified - no database, no decorators, just pure functions
"""
import random
from typing import List
from pathlib import Path

import numpy as np
from PIL import Image

from .image_utils import ImageUtils


DATA_DIR = Path(__file__).parent / "data"


def get_pet_frames(avatar: Image.Image) -> list:
    """Generate frames for pet GIF animation (vlcice_gif version - 14 frames)"""
    width, height = 148, 148
    vertical_offset = (0, 0, 0, 0, 1, 2, 3, 4, 5, 4, 3, 2, 2, 1, 0)
    
    frames = []
    avatar = ImageUtils.round_image(avatar.resize((100, 100), Image.LANCZOS).convert("RGBA"))
    
    for i in range(14):
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        img = f"{i + 1:02d}"
        try:
            frame_object = Image.open(DATA_DIR / f"pet/{img}.png")
            frame.paste(avatar, (35, 25 + vertical_offset[i]), avatar)
            frame.paste(frame_object, (10, 5), frame_object)
        except FileNotFoundError:
            frame.paste(avatar, (35, 25 + vertical_offset[i]), avatar)
        frames.append(frame)
    
    return frames


def get_hyperpet_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the hyperpet animation"""
    frames = []
    width, height = 148, 148
    vertical_offset = (0, 1, 2, 3, 1, 0)

    avatar = ImageUtils.round_image(avatar.resize((100, 100)))
    avatar_pixels = np.array(avatar)

    for i in range(6):
        img = f"{i + 1:02d}"
        deform_hue = random.randint(0, 99) ** (i + 1) // 100**i / 100
        frame_avatar = Image.fromarray(
            ImageUtils.shift_hue(avatar_pixels, deform_hue)
        )
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"hyperpet/{img}.png")
            frame.paste(frame_avatar, (35, 25 + vertical_offset[i]), frame_avatar)
            frame.paste(frame_object, (10, 5), frame_object)
        except FileNotFoundError:
            # Fallback
            frame.paste(frame_avatar, (35, 25 + vertical_offset[i]), frame_avatar)
        frames.append(frame)

    return frames


def get_bonk_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the bonk animation"""
    frames = []
    width, height = 200, 170
    deformation = (0, 0, 0, 5, 10, 20, 15, 5)

    avatar = ImageUtils.round_image(avatar.resize((100, 100)))

    for i in range(8):
        img = f"{i + 1:02d}"
        frame_avatar = avatar.resize((100, 100 - deformation[i]))
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"bonk/{img}.png")
            frame.paste(frame_avatar, (80, 60 + deformation[i]), frame_avatar)
            frame.paste(frame_object, (10, 5), frame_object)
        except FileNotFoundError:
            # Fallback
            frame.paste(frame_avatar, (80, 60 + deformation[i]), frame_avatar)
        frames.append(frame)

    return frames


def get_whip_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the whip animation"""
    frames = []
    width, height = 250, 150
    deformation = [0] * 8 + [2, 3, 5, 9, 6, 4, 3, 0] + [0] * 10
    translation = [0] * 9 + [1, 2, 2, 3, 3, 3, 2, 1] + [0] * 9

    avatar = ImageUtils.round_image(avatar.resize((100, 100)))

    for i in range(26):
        img = f"{i + 1:02d}"
        frame_avatar = avatar.resize((100 - deformation[i], 100))
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"whip/{img}.png").resize((150, 150))
            frame.paste(
                frame_avatar, (135 + deformation[i] + translation[i], 25), frame_avatar
            )
            frame.paste(frame_object, (0, 0), frame_object)
        except FileNotFoundError:
            # Fallback
            frame.paste(
                frame_avatar, (135 + deformation[i] + translation[i], 25), frame_avatar
            )
        frames.append(frame)

    return frames


def get_spank_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the spank animation"""
    frames = []
    width, height = 200, 120
    deformation = (4, 2, 1, 0, 0, 0, 0, 3)

    avatar = ImageUtils.round_image(avatar.resize((100, 100)))

    for i in range(8):
        img = f"{i + 1:02d}"
        frame_avatar = avatar.resize(
            (100 + 2 * deformation[i], 100 + 2 * deformation[i])
        )
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"spank/{img}.png").resize((100, 100))
            frame.paste(frame_object, (10, 15), frame_object)
            frame.paste(
                frame_avatar, (80 - deformation[i], 10 - deformation[i]), frame_avatar
            )
        except FileNotFoundError:
            # Fallback
            frame.paste(
                frame_avatar, (80 - deformation[i], 10 - deformation[i]), frame_avatar
            )
        frames.append(frame)

    return frames


def get_lick_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the lick animation"""
    frames = []
    width, height = 270, 136
    voffset = (0, 2, 1, 2)
    hoffset = (-2, 0, 2, 0)

    avatar = ImageUtils.round_image(avatar.resize((64, 64)))

    for i in range(4):
        img = ("01", "02", "03", "02")[i]
        frame_avatar = avatar.resize((64, 64))
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"lick/{img}.png")
            frame.paste(frame_object, (10, 15), frame_object)
            frame.paste(frame_avatar, (198 + voffset[i], 68 + hoffset[i]), frame_avatar)
        except FileNotFoundError:
            # Fallback
            frame.paste(frame_avatar, (198 + voffset[i], 68 + hoffset[i]), frame_avatar)
        frames.append(frame)

    return frames


def get_hyperlick_frames(avatar: Image.Image) -> List[Image.Image]:
    """Get frames for the hyperlick animation"""
    frames = []
    width, height = 270, 136
    voffset = (0, 3, -1, 3)
    hoffset = (-2, 0, 2, 0)

    avatar = ImageUtils.round_image(avatar.resize((64, 64)))
    avatar_pixels = np.array(avatar)

    for i in range(4):
        img = ("01", "02", "03", "02")[i]
        deform_hue = random.randint(0, 99) ** (i + 1) // 100**i / 100
        frame_avatar = Image.fromarray(
            ImageUtils.shift_hue(avatar_pixels, deform_hue)
        )
        
        frame = Image.new("RGBA", (width, height), (54, 57, 63, 0))
        try:
            frame_object = Image.open(DATA_DIR / f"lick/{img}.png")
            frame.paste(frame_object, (10, 15), frame_object)
            frame.paste(frame_avatar, (198 + voffset[i], 68 + hoffset[i]), frame_avatar)
        except FileNotFoundError:
            # Fallback
            frame.paste(frame_avatar, (198 + voffset[i], 68 + hoffset[i]), frame_avatar)
        frames.append(frame)

    return frames
