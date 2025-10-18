# Adapted GIF Cog for Tockar Discord Bot
# Original from RubberGod: https://github.com/vutfitdiscord/rubbergod/tree/main/cogs/gif

"""
Cog for creating GIF animations.
"""

from io import BytesIO
from typing import Optional
import discord
from discord.ext import commands
from PIL import Image

from .features import ImageHandler
from config import load_config


class GifCog(commands.Cog):
    """Discord cog for GIF animation commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.imagehandler = ImageHandler()
        self.config = load_config()

    def _check_permissions(self, user_id: int) -> bool:
        """Check if user has permission to use commands."""
        return not self.config.users.allowed_ids or user_id in self.config.users.allowed_ids

    async def get_profile_picture(self, user: discord.User, size: Optional[int] = None, format: str = "png") -> Image.Image:
        """Get a user's profile picture as a PIL Image."""
        if size is not None:
            avatar_data = await user.display_avatar.replace(size=size, format=format).read()
        else:
            avatar_data = await user.display_avatar.replace(format=format).read()
        
        avatar_image = Image.open(BytesIO(avatar_data)).convert("RGBA")
        return avatar_image

    @discord.app_commands.command(name="pet", description="Pohlaď někoho! 🐾")
    async def pet(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """Create a pet GIF animation with the user's avatar."""
        # Check permissions
        if not self._check_permissions(interaction.user.id):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        target_user = user or interaction.user
        
        avatar = await self.get_profile_picture(target_user)
        frames = ImageHandler.get_pet_frames(avatar)

        with BytesIO() as image_binary:
            frames[0].save(
                image_binary,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=40,
                loop=0,
                transparency=0,
                disposal=2,
                optimize=False,
            )
            image_binary.seek(0)
            
            await interaction.followup.send(
                file=discord.File(fp=image_binary, filename="pet.gif")
            )

    @discord.app_commands.command(name="bonk", description="Bonkni někoho! 🔨")
    async def bonk(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """Create a bonk GIF animation with the user's avatar."""
        # Check permissions
        if not self._check_permissions(interaction.user.id):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        target_user = user or interaction.user
        
        avatar = await self.get_profile_picture(target_user)
        frames = ImageHandler.get_bonk_frames(avatar)

        with BytesIO() as image_binary:
            frames[0].save(
                image_binary,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=30,
                loop=0,
                disposal=2,
                optimize=False,
            )
            image_binary.seek(0)
            
            await interaction.followup.send(
                file=discord.File(fp=image_binary, filename="bonk.gif")
            )

    @discord.app_commands.command(name="catnap", description="Ukradni někoho! 😴")
    async def catnap(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """Create a catnap/steal GIF animation with the user's avatar."""
        # Check permissions
        if not self._check_permissions(interaction.user.id):
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        target_user = user or interaction.user
        
        avatar = await self.get_profile_picture(target_user, 64)

        # Ensure correct size
        width, height = avatar.size
        if width != 64 or height != 64:
            avatar = avatar.resize((64, 64))

        # Process avatar
        avatar = avatar.convert("P", palette=Image.Resampling.LANCZOS, colors=200).convert("RGBA")
        avatar = self.imagehandler.square_to_circle(avatar)
        avatar = avatar.convert("P", palette=Image.Resampling.LANCZOS, colors=200).convert("RGBA")
        
        with BytesIO() as image_binary:
            ImageHandler.render_catnap(image_binary, avatar)
            
            await interaction.followup.send(
                file=discord.File(fp=image_binary, filename="catnap.gif")
            )


async def setup(bot: commands.Bot):
    """Setup function for loading the cog."""
    await bot.add_cog(GifCog(bot))