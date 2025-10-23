"""Configuration management using environ-config."""
import environ


@environ.config(prefix="DISCORD")
class BotConfig:
    """Discord bot configuration."""
    
    @environ.config
    class Bot:
        """Bot-specific configuration."""
        token = environ.var(help="Discord bot token")
        prefix = environ.var(default="!", help="Command prefix")
        startup_channel_id = environ.var(
            default=None,
            converter=lambda x: int(x) if x else None,
            help="Channel ID to send startup message"
        )
        
    @environ.config
    class Guild:
        """Guild-specific configuration."""
        ids = environ.var(
            default=None, 
            converter=lambda x: [int(id.strip()) for id in x.split(',')] if x else None, 
            help="Comma-separated Guild IDs for development (e.g., '123456789,987654321')"
        )
    
    @environ.config
    class Users:
        """User-specific configuration."""
        elevated_ids = environ.var(
            default=None,
            converter=lambda x: [int(id.strip()) for id in x.split(',')] if x else None,
            help="Comma-separated User IDs with elevated permissions (e.g., '123456789,987654321')"
        )
        blocked_ids = environ.var(
            default=None,
            converter=lambda x: [int(id.strip()) for id in x.split(',')] if x else None,
            help="Comma-separated User IDs that are blocked from using bot commands"
        )
    
    bot = environ.group(Bot)
    guild = environ.group(Guild)
    users = environ.group(Users)


def load_config() -> BotConfig:
    """Load configuration from environment variables.
    
    Returns:
        BotConfig: Loaded configuration object.
    """
    return environ.to_config(BotConfig)
