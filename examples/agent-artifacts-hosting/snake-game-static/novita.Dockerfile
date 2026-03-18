# Sandbox template: only for storing source code
# Dockerfile will be used to build production image during deployment

FROM ubuntu:22.04

# Set working directory
# Set working directory
WORKDIR /app

# Copy website source files to template
# Copy website source files to template
COPY . .
