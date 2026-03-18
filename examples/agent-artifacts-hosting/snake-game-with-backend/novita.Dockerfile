FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Node.js 20
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack and install pnpm (matching packageManager version)
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

WORKDIR /app

# Copy source code to image
COPY . .

# Pre-install pnpm dependencies (speeds up subsequent deployment builds)
RUN pnpm install
