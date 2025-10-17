# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies and fonts with Czech support
RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto \
    fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy wheelspin project first (from parent context)
COPY wheelspin-gif-python /wheelspin-gif-python

# Copy bot project files
COPY tockar-discord-bot/pyproject.toml ./

# Install wheelspin in editable mode
RUN uv pip install -e /wheelspin-gif-python

# Install other dependencies
RUN uv pip install -r pyproject.toml

# Copy rest of application code
COPY tockar-discord-bot/. .

# Run the bot
CMD ["python", "app.py"]
