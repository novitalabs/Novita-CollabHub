FROM ubuntu:22.04

# Set non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    net-tools \
    bash \
    ca-certificates \
    libglib2.0-0 \
    libdbus-1-3 \
    libx11-6 \
    libxcb1 \
    libexpat1 \
    libfontconfig1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    # Chinese language and font support: \
    locales \
    language-pack-zh-hans \
    language-pack-zh-hant \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy scripts directory
COPY scripts/ /app/scripts/

# Set script permissions
RUN chmod +x /app/scripts/*.sh

# Download Chromium
RUN cd /app/scripts && bash ./update.sh

# Copy pre-compiled WebSocket proxy binary
COPY reverse-proxy /app/reverse-proxy
RUN chmod +x /app/reverse-proxy

# Create browser-use directory
RUN mkdir -p /app/.browser-use

# Copy startup script
COPY start-up.sh /app/.browser-use/start-up.sh

# Set startup script permissions
RUN chmod +x /app/.browser-use/start-up.sh

# Create user data directory
RUN mkdir -p /app/user-data-dir
