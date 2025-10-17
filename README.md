# Tockar Discord Bot

A Discord bot built with discord.py, using environ-config for configuration management and Docker for deployment.

## Features

- 🤖 Built with discord.py
- ⚙️ Environment-based configuration using environ-config
- 🐳 Docker and Docker Compose support
- 📦 Dependency management with uv
- 🎯 Basic commands included (ping, hello)

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (for local development)
- Docker and Docker Compose (for containerized deployment)
- A Discord bot token (see [Creating a Bot Account](#creating-a-bot-account))

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd tockar-discord-bot
```

### 2. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_BOT_PREFIX=!
```

### 3. Running with Docker (Recommended)

Build and start the bot:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

Stop the bot:

```bash
docker-compose down
```

### 4. Running locally

Install dependencies:

```bash
uv sync
```

Run the bot:

```bash
uv run python main.py
```

## Creating a Bot Account

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy" to get your bot token
6. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
   - PRESENCE INTENT (optional)
7. Go to "OAuth2" > "URL Generator"
8. Select scopes: `bot`, `applications.commands`
9. Select bot permissions you need (e.g., Send Messages, Read Messages)
10. Copy the generated URL and open it in your browser to invite the bot to your server

## Available Commands

- `!ping` - Check bot latency
- `!hello` - Get a greeting from the bot

## Configuration

The bot uses environ-config for configuration management. All configuration is loaded from environment variables:

- `DISCORD_BOT_TOKEN` (required) - Your Discord bot token
- `DISCORD_BOT_PREFIX` (optional, default: `!`) - Command prefix
- `DISCORD_GUILD_ID` (optional) - Guild ID for faster command syncing during development

## Project Structure

```
tockar-discord-bot/
├── main.py              # Bot entry point
├── config.py            # Configuration management
├── pyproject.toml       # Project dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Development

To add new commands, edit `main.py` and add command decorators:

```python
@bot.command(name="mycommand")
async def my_command(ctx: commands.Context):
    """Description of your command."""
    await ctx.send("Response!")
```

For more complex bots, consider organizing commands into cogs (extensions).

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
