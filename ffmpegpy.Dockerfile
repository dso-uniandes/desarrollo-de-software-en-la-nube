# syntax=docker/dockerfile:1.6
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Single-layer, no cache mounts -> no locks
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Optional: minimal test
RUN ffmpeg -version | head -n 1