"""Discord bot main entry point."""

import asyncio
import functools
import logging
import random
import time
from datetime import timedelta
from io import BytesIO

import discord
import wheelspin
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image

from config import load_config, BotConfig
from rubbergod_gif.features import ImageHandler
from vlcice_gif import (
    create_transparent_gif,
    get_hyperlick_frames,
    get_hyperpet_frames,
    get_lick_frames,
    get_pet_frames,
    get_spank_frames,
    get_users_avatar,
    get_whip_frames,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def time_command(operation_name: str):
    """Decorator to time command execution and send ephemeral timing info."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time

            # Send timing info as ephemeral message
            # Get interaction from the first argument (after self if it exists)
            interaction = args[0] if args else kwargs.get("interaction")
            if interaction and hasattr(interaction, "followup"):
                try:
                    await interaction.followup.send(
                        content=f"⏱️ {operation_name} dokončena za {execution_time:.2f} sekund",
                        ephemeral=True,
                    )
                except Exception as e:
                    logger.warning(f"Failed to send timing info: {e}")

            return result

        return wrapper

    return decorator


def require_elevated_permissions(config):
    """Decorator to check if user has elevated permissions (user ID or role)."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            # Check if user has elevated permissions by user ID
            if config.users.elevated_ids and interaction.user.id in config.users.elevated_ids:
                return await func(interaction, *args, **kwargs)
            
            # Check if user has elevated permissions by role
            if config.users.elevated_roles and interaction.guild:
                member = interaction.guild.get_member(interaction.user.id)
                if member:
                    user_role_ids = [role.id for role in member.roles]
                    if any(role_id in user_role_ids for role_id in config.users.elevated_roles):
                        return await func(interaction, *args, **kwargs)
            
            # If no elevated IDs/roles configured, allow anyone
            if not config.users.elevated_ids and not config.users.elevated_roles:
                return await func(interaction, *args, **kwargs)
            
            # User doesn't have elevated permissions
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!", ephemeral=True
            )
            return

        return wrapper
    return decorator


class TockarBot(commands.Bot):
    """Custom Discord bot class."""
    _startup_complete = False  # Flag to track if startup has been completed

    def __init__(self, guild_ids=None, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_ids = guild_ids or []
        self.config: BotConfig = config

    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot is starting up...")
        logger.info(f"Using config: {self.config}")
        
        # Add interaction check for blocked users
        self.tree.interaction_check = self._global_interaction_check
        
        # Sync slash commands with Discord
        try:
            if self.guild_ids:
                # Sync to specific guilds for instant updates (development)
                for guild_id in self.guild_ids:
                    guild = discord.Object(id=guild_id)
                    self.tree.copy_global_to(guild=guild)
                    synced = await self.tree.sync(guild=guild)
                    logger.info(f"Synced {len(synced)} command(s) to guild {guild_id}")
            else:
                # Sync globally (takes up to 1 hour)
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s) globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def _global_interaction_check(self, interaction: discord.Interaction) -> bool:
        """Global check for all interactions to block certain users."""
        if self.config and self.config.users.blocked_ids:
            if interaction.user.id in self.config.users.blocked_ids:
                await interaction.response.send_message(
                    "🚫 Nemáš povolení používat tohoto bota.",
                    ephemeral=True
                )
                logger.info(f"Blocked user {interaction.user.id} ({interaction.user.name}) attempted to use command")
                return False
        return True

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Skip startup message if already completed
        if self._startup_complete:
            logger.info("Bot reconnected (startup message already sent)")
            logger.info("------")
            return

        self._startup_complete = True
        
        # Send startup message only on first ready event
        await self._send_startup_message()
        
        # Mark startup as complete
        logger.info("Startup sequence completed")
        logger.info("------")

    async def _send_startup_message(self):
        """Send startup message to configured channel."""
        if not self.config or not self.config.bot.startup_channel_id:
            logger.warning("No startup channel configured")
            return

        try:
            channel = self.get_channel(self.config.bot.startup_channel_id)
            if not channel:
                logger.warning(f"Startup channel {self.config.bot.startup_channel_id} not found")
                return

            if not discord.Permissions.moderate_members:
                await channel.send(
                    "⚠️ Upozornění: Bot nemá oprávnění pro správu členů, "
                    "některé funkce nemusí fungovat správně."
                )
            await channel.send("✅ Bot byl spuštěn!")
            
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")

    async def on_message(self, message: discord.Message):
        """Called when a message is received."""
        # Don't respond to ourselves
        if message.author == self.user:
            return

        # Process commands
        await self.process_commands(message)


async def main():
    """Main function to run the bot."""
    # Load environment variables from .env file
    load_dotenv()

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True

    # Create bot instance
    bot = TockarBot(
        guild_ids=config.guild.ids,
        config=config,
        command_prefix=config.bot.prefix,
        intents=intents,
        help_command=commands.DefaultHelpCommand(),
    )

    @bot.tree.command(
        name="tocka", description="Roztočí kolo štěstí a vybere náhodného výherce!"
    )
    @require_elevated_permissions(config)
    @time_command("Točka")
    async def tocka(interaction: discord.Interaction):
        """Slash command to spin the wheel and pick a winner."""
        # Defer the response since creating the GIF might take time
        await interaction.response.defer()

        # Get list of members in the voice channel or text channel
        channel = interaction.channel

        # Try to get members from voice channel if user is in one
        if interaction.user.voice and interaction.user.voice.channel:
            members = interaction.user.voice.channel.members
        else:
            # Otherwise use text channel members
            members = channel.members

        # Filter out bots and get display names
        member_names = [member.display_name for member in members if not member.bot]

        if not member_names:
            await interaction.followup.send("❌ Nejsou žádní uživatelé k výběru!")
            return

        # Create the spinning wheel GIF
        winner = wheelspin.create_spinning_wheel(
            member_names, output_file="tocka_wheel.gif"
        )

        # Send the result
        await interaction.followup.send(
            content=f"🎉 **{winner}** vyhrál/a Točku! 🎉",
            file=discord.File("tocka_wheel.gif"),
        )

    @bot.tree.command(
        name="tocka-roles",
        description="Roztočí kolo štěstí pouze s uživateli, kteří mají specifickou roli!",
    )
    @require_elevated_permissions(config)
    @time_command("Točka")
    async def tocka_roles(interaction: discord.Interaction):
        """Slash command to spin the wheel with only members who have roles."""
        # Defer the response since creating the GIF might take time
        await interaction.response.defer()

        # Get list of members in the voice channel or text channel
        channel = interaction.channel

        # Try to get members from voice channel if user is in one
        if interaction.user.voice and interaction.user.voice.channel:
            members = interaction.user.voice.channel.members
        else:
            # Otherwise use text channel members
            members = channel.members

        # Filter out bots AND members who only have @everyone role or specific roles
        member_names = []
        target_role_ids = config.roles.tocka if config.roles.tocka else None
        
        if target_role_ids:
            # Check if member has any of the specified roles
            for member in members:
                if not member.bot:
                    member_role_ids = [role.id for role in member.roles]
                    if any(role_id in member_role_ids for role_id in target_role_ids):
                        member_names.append(member.display_name)
        else:
            # Fallback: check if member has any role other than @everyone
            for member in members:
                if not member.bot:
                    member_roles = [
                        role for role in member.roles if role.name != "@everyone"
                    ]
                    if member_roles:  # Only include if they have at least one role
                        member_names.append(member.display_name)

        if not member_names:
            await interaction.followup.send(
                "❌ Nejsou žádní uživatelé s rolemi k výběru!"
            )
            return

        # Create the spinning wheel GIF
        winner = wheelspin.create_spinning_wheel(
            member_names, output_file="tocka_wheel.gif"
        )

        # Send the result
        await interaction.followup.send(
            content=f"🎉 **{winner}** vyhrál/a Točku! 🎉",
            file=discord.File("tocka_wheel.gif"),
        )

    @bot.tree.command(
        name="tocka-vlastni", description="Roztočí kolo štěstí s vlastními možnostmi!"
    )
    @discord.app_commands.describe(
        options="Seznam možností oddělených čárkami (např: 'Možnost 1, Možnost 2, Možnost 3')",
        separator="Oddělovač možností (výchozí: čárka)",
    )
    @discord.app_commands.choices(
        separator=[
            discord.app_commands.Choice(name="Čárka (,)", value=","),
            discord.app_commands.Choice(name="Středník (;)", value=";"),
            discord.app_commands.Choice(name="Nový řádek", value="\n"),
            discord.app_commands.Choice(name="Mezera ( )", value=" "),
        ]
    )
    @time_command("Točka")
    async def tocka_vlastni(
        interaction: discord.Interaction, options: str, separator: str = ","
    ):
        """Slash command to spin the wheel with custom input."""
        # Defer the response since creating the GIF might take time
        await interaction.response.defer()

        # Parse the options string
        option_list = [
            option.strip() for option in options.split(separator) if option.strip()
        ]

        # Validate input
        if not option_list:
            await interaction.followup.send("❌ Žádné platné možnosti nebyly zadány!", ephemeral=True)
            return

        if len(option_list) < 2:
            await interaction.followup.send("❌ Musíš zadat alespoň 2 možnosti!", ephemeral=True)
            return

        if len(option_list) > 100:
            await interaction.followup.send("❌ Příliš mnoho možností! Maximum je 100.", ephemeral=True)
            return

        # Create the spinning wheel GIF with frame limit
        winner = wheelspin.create_spinning_wheel(
            option_list,
            output_file="tocka_wheel.gif",
        )

        # Send the result
        await interaction.followup.send(
            content=f"🎉 **{winner}**! 🎉", file=discord.File("tocka_wheel.gif")
        )

    @bot.tree.command(name="cudlik", description="Ukáž délku svého čudlíku!")
    async def cudlik(interaction: discord.Interaction):
        length = random.randint(0, 25)
        await interaction.response.send_message(f"Tvůj čudlík má délku: {length} cm")

    @bot.tree.command(name="ping", description="Odpovědí pong!")
    async def ping(interaction: discord.Interaction):
        """Simple ping command that responds with pong (ephemeral)."""
        await interaction.response.send_message("🏓 Pong!", ephemeral=True)

    # Helper function to get profile picture
    async def get_profile_picture(user: discord.User, size=None, format="png"):
        """Get a user's profile picture as a PIL Image."""
        if size is not None:
            avatar_data = await user.display_avatar.replace(
                size=size, format=format
            ).read()
        else:
            avatar_data = await user.display_avatar.replace(format=format).read()

        avatar_image = Image.open(BytesIO(avatar_data)).convert("RGBA")
        return avatar_image

    # Simple GIF commands using the ImageHandler
    @bot.tree.command(name="pet", description="Pohlaď někoho! 🐾")
    async def pet(interaction: discord.Interaction, user: discord.User = None):
        """Pet someone with animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_profile_picture(target_user)
            frames = ImageHandler.get_pet_frames(avatar)

            image_binary = BytesIO()
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
                file=discord.File(image_binary, filename="pet.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="bonk", description="Bonkni někoho! 🔨")
    async def bonk(interaction: discord.Interaction, user: discord.User = None):
        """Bonk someone with animated GIF."""
        await interaction.response.defer()
        
        target_user = user or interaction.user
        
        # 50% chance to timeout the command caller instead of bonking
        if random.choice([True, False, False]) and interaction.guild:
            try:
                # Get the caller's member object
                caller_member = interaction.guild.get_member(interaction.user.id)
                if not caller_member:
                    logger.warning(f"Could not find caller member {interaction.user.id} in guild")
                else:
                    # Check if bot has permission to timeout
                    bot_member = interaction.guild.get_member(interaction.client.user.id)
                    if not bot_member.guild_permissions.moderate_members:
                        await interaction.followup.send(
                            "⚠️ Bot nemá oprávnění 'Moderate Members' pro timeout!",
                        )
                    # Check if caller is not higher than bot
                    elif caller_member.top_role < bot_member.top_role:
                        # Perform timeout on the caller
                        timeout_length_minutes = 5
                        await caller_member.timeout(
                            timedelta(minutes=timeout_length_minutes), 
                            reason="Bonk backfired!"
                        )
                        await interaction.followup.send(
                            f"💥 Bonk se obrátil proti tobě! {caller_member.display_name} byl timeoutován na {timeout_length_minutes} minut! ⏲️"
                        )
                        # Don't send GIF, just return
                        return
                    else:
                        logger.info(
                            f"Cannot timeout caller {caller_member.id} due to role hierarchy."
                        )
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ Nemám oprávnění timeoutovat tohoto uživatele!",
                    ephemeral=True
                )
            except Exception as e:
                logger.error(f"Failed to timeout user: {e}")
                await interaction.followup.send(
                    f"❌ Chyba při timeoutování: {e}",
                    ephemeral=True
                )

        # Send bonk GIF
        try:
            avatar = await get_profile_picture(target_user)
            frames = ImageHandler.get_bonk_frames(avatar)

            image_binary = BytesIO()
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
                file=discord.File(image_binary, filename="bonk.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(
        name="pet-subtle", description="Pohlaď někoho (vlcice verze)! 🐾✨"
    )
    async def pet_vlcice(interaction: discord.Interaction, user: discord.User = None):
        """Pet someone with vlcice_gif animated GIF (14 frames)."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_pet_frames(avatar)
            gif_binary = create_transparent_gif(frames, duration=40)

            await interaction.followup.send(
                file=discord.File(gif_binary, filename="pet-vlcice.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="catnap", description="Ukradni někoho! 😴")
    async def catnap(interaction: discord.Interaction, user: discord.User = None):
        """Catnap someone with animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_profile_picture(target_user, 64)
            if avatar.size != (64, 64):
                avatar = avatar.resize((64, 64))

            avatar = ImageHandler.square_to_circle(avatar)

            image_binary = BytesIO()
            ImageHandler.render_catnap(image_binary, avatar)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="catnap.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="whip", description="Ošlehej někoho bičem! 🞭")
    async def whip(interaction: discord.Interaction, user: discord.User = None):
        """Whip someone with animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_whip_frames(avatar)
            image_binary = create_transparent_gif(frames, duration=30)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="whip.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="spank", description="Dej někomu facku! 👋")
    async def spank(interaction: discord.Interaction, user: discord.User = None):
        """Spank someone with animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_spank_frames(avatar)
            image_binary = create_transparent_gif(frames, duration=30)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="spank.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="lick", description="Olízni někoho! 👅")
    async def lick(interaction: discord.Interaction, user: discord.User = None):
        """Lick someone with animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_lick_frames(avatar)
            image_binary = create_transparent_gif(frames, duration=30)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="lick.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="hyperlick", description="Olízni někoho psychedelicky! 🌈👅")
    async def hyperlick(interaction: discord.Interaction, user: discord.User = None):
        """Lick someone with psychedelic animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_hyperlick_frames(avatar)
            image_binary = create_transparent_gif(frames, duration=30)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="hyperlick.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    @bot.tree.command(name="hyperpet", description="Pohlaď někoho psychedelicky! 🌈🐾")
    async def hyperpet_cmd(interaction: discord.Interaction, user: discord.User = None):
        """Pet someone with psychedelic animated GIF."""
        await interaction.response.defer()
        target_user = user or interaction.user

        try:
            avatar = await get_users_avatar(target_user)
            frames = get_hyperpet_frames(avatar)
            image_binary = create_transparent_gif(frames, duration=30)

            await interaction.followup.send(
                file=discord.File(image_binary, filename="hyperpet.gif")
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Chyba při vytváření GIF: {e}")

    # Start the bot
    try:
        logger.info("Starting bot...")
        async with bot:
            await bot.start(config.bot.token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
