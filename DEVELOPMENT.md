# Dynamic Wheelspin Development Setup

## Overview
The bot now uses the local `wheelspin-gif-python` project in editable/development mode. This means any changes you make to the wheelspin project will be immediately reflected without needing to rebuild and reinstall.

## Setup Structure

```
Repositories/
├── tockar-discord-bot/          # This bot project
│   ├── main.py
│   ├── config.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── docker-compose.yml
└── wheelspin-gif-python/        # Your wheelspin library
    ├── wheelspin/
    ├── pyproject.toml
    └── ...
```

## How It Works

### For Local Development

The wheelspin package is installed in editable mode:
```bash
uv pip install -e ../wheelspin-gif-python
```

**Benefits:**
- Changes to wheelspin code are immediately available
- No need to rebuild or reinstall
- Perfect for development and testing

### For Docker

The `docker-compose.yml` uses a parent build context to include both projects:
```yaml
build:
  context: ..                              # Parent directory
  dockerfile: tockar-discord-bot/Dockerfile
```

The `Dockerfile` installs wheelspin in editable mode inside the container:
```dockerfile
COPY wheelspin-gif-python /wheelspin-gif-python
RUN uv pip install -e /wheelspin-gif-python
```

**Benefits:**
- Both projects are available in the container
- Wheelspin is installed as editable
- Clean separation of concerns

## Usage

### Local Development
```bash
# Make changes to wheelspin-gif-python
cd ../wheelspin-gif-python
# Edit files...

# Run the bot - changes are immediately available
cd ../tockar-discord-bot
uv run python main.py
```

### Docker Development
```bash
# Rebuild when you make changes to wheelspin
docker compose up --build

# Or just restart if only bot code changed
docker compose restart
```

## Commands

### Local Development
```bash
# Install/update wheelspin in editable mode
uv pip install -e ../wheelspin-gif-python

# Run bot locally
uv run python main.py
```

### Docker
```bash
# Build and run
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down
```

## Slash Command

The bot now uses Discord's slash command API instead of prefix commands:

- Old: `!tocka`
- New: `/tocka`

The command will:
1. Check if you're in a voice channel and use those members
2. Fall back to text channel members if not
3. Create a spinning wheel GIF
4. Announce the winner in Czech: "🎉 **{winner}** vyhrál Točku! 🎉"

## Notes

- The wheelspin package doesn't need to be in `pyproject.toml` dependencies since it's installed separately in editable mode
- Any changes to wheelspin require a Docker rebuild: `docker compose up --build`
- For local development, wheelspin changes are immediate (no rebuild needed)
