"""Discord bot main entry point."""
import asyncio
import logging
import time

import discord
import wheelspin
from discord.ext import commands
from dotenv import load_dotenv

from config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TockarBot(commands.Bot):
    """Custom Discord bot class."""
    
    def __init__(self, guild_ids=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_ids = guild_ids or []
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot is starting up...")
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
        
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info("------")
        
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
        command_prefix=config.bot.prefix,
        intents=intents,
        help_command=commands.DefaultHelpCommand()
    )
    
    @bot.tree.command(name="tocka", description="Roztočí kolo štěstí a vybere náhodného výherce!")
    async def tocka(interaction: discord.Interaction):
        """Slash command to spin the wheel and pick a winner."""
        # Check if user is allowed to use commands
        if config.users.allowed_ids and interaction.user.id not in config.users.allowed_ids:
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!",
                ephemeral=True
            )
            return
        
        # Start timing
        start_time = time.time()
        
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
            member_names,
            output_file="tocka_wheel.gif"
        )
        
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Send the result
        await interaction.followup.send(
            content=f"🎉 **{winner}** vyhrál Točku! 🎉",
            file=discord.File("tocka_wheel.gif")
        )
        
        # Send timing info as ephemeral message
        await interaction.followup.send(
            content=f"⏱️ Generace točky trvala {execution_time:.2f} sekund",
            ephemeral=True
        )

    @bot.tree.command(name="tocka-roles", description="Roztočí kolo štěstí pouze s uživateli, kteří mají nějakou roli!")
    async def tocka_roles(interaction: discord.Interaction):
        """Slash command to spin the wheel with only members who have roles."""
        # Check if user is allowed to use commands
        if config.users.allowed_ids and interaction.user.id not in config.users.allowed_ids:
            await interaction.response.send_message(
                "❌ Nemáš oprávnění použít tento příkaz!",
                ephemeral=True
            )
            return
        
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
        
        # Filter out bots AND members who only have @everyone role
        member_names = []
        for member in members:
            if not member.bot:
                # Check if member has any role other than @everyone
                member_roles = [role for role in member.roles if role.name != "@everyone"]
                if member_roles:  # Only include if they have at least one role
                    member_names.append(member.display_name)
        
        if not member_names:
            await interaction.followup.send("❌ Nejsou žádní uživatelé s rolemi k výběru!")
            return
        
        # Create the spinning wheel GIF
        winner = wheelspin.create_spinning_wheel(
            member_names,
            output_file="tocka_wheel.gif"
        )
        
        # Send the result
        await interaction.followup.send(
            content=f"🎉 **{winner}** vyhrál Točku! (pouze uživatelé s rolemi) 🎉",
            file=discord.File("tocka_wheel.gif")
        )

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
