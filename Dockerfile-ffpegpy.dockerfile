# syntax=docker/dockerfile:1.8
FROM python:3.13-slim

# Avoid interactive tzdata prompts, speed up pip, fewer .pyc files
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install ffmpeg (and minimal tools), then clean up apt cache
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# (Optional) install your Python deps
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# (Optional) copy your app
# COPY . .

# Quick self-check (shows ffmpeg version at build time)
# Remove this if you don’t want extra layers/log noise.
RUN ffmpeg -version | head -n 1
