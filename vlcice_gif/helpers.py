"""
Helper functions for vlcice_gif module
Simple replacements for removed dependencies
"""
import aiohttp
from io import BytesIO
from typing import List, Union
from PIL import Image
import discord

from .image_utils import ImageUtils


async def get_users_avatar(user: discord.User, size: int = 256) -> Image.Image:
    """Get a user's avatar as PIL Image."""
    url = user.display_avatar.replace(size=size).url
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        if response.status != 200:
            raise discord.HTTPException(response, "Avatar could not be fetched.")
        content = BytesIO(await response.read())
    avatar = Image.open(content).convert("RGBA")
    return avatar


def create_transparent_gif(frames: List[Image.Image], duration: Union[int, List[int]]) -> BytesIO:
    """
    Create a transparent GIF with proper transparency handling.
    Uses ImageUtils.create_animated_gif for proper GifConverter processing.
    """
    image_binary = BytesIO()
    output_image, save_kwargs = ImageUtils.create_animated_gif(frames, duration)
    output_image.save(image_binary, **save_kwargs)
    image_binary.seek(0)
    return image_binary
