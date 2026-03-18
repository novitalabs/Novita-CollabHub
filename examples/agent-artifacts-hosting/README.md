# Novita Artifact Hosting - Deployment Examples

This repository contains example projects and deployment scripts for [Novita Artifact Hosting](https://novita.ai), a platform for deploying web applications with a single API call.

## Overview

Novita Artifact Hosting allows you to deploy containerized web applications from sandbox environments. The deployment process involves:

1. **Create a Sandbox** - Start from a pre-configured template containing your source code
2. **Create a Project** - Register your application and get a deployment URL
3. **Deploy** - Build a Docker image and deploy it to the cloud

## Prerequisites

- Python 3.8+
- Novita Sandbox CLI (`pip install novita-sandbox`)
- A Novita API key ([Get one here](https://novita.ai))

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Build a Sandbox Template

First, navigate to your project directory and build a sandbox template. The template packages your source code into a reusable environment.

```bash
cd ecomm-with-sql
novita-sandbox-cli template build -d ./novita.Dockerfile -n ecomm-with-sql
```

- `-d` specifies the Dockerfile used to build the template
- `-n` specifies the template name (you'll use this in the next step)

Each example project includes a `novita.Dockerfile` for building templates.

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Required
NOVITA_API_KEY=your-api-key

# Optional (depending on your app)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Run the Deployment Script

```bash
python app.py --template ecomm-with-sql --project-name my-webapp --dockerfile ecomm-with-sql/Dockerfile
```

Available arguments:

| Argument | Description |
|----------|-------------|
| `--template` | Sandbox template name (from step 1) |
| `--project-name` | Project name, used in the deployment URL |
| `--dockerfile` | Path to Dockerfile, relative to this script |
| `--http-port` | HTTP port the app listens on (default: 3000, use 80 for Nginx) |
| `--sandbox-timeout` | Sandbox timeout in seconds (default: 600) |
| `-v` | Enable debug logging |

The script will:
- Create a sandbox from your template
- Create or reuse a project with the specified name
- Deploy your application using the Dockerfile
- Stream build logs in real-time
- Output the deployment URL when complete

### Example Output

```
Deploying [my-webapp] with template [ecomm-with-sql]
  Dockerfile: /path/to/ecomm-with-sql/Dockerfile
  HTTP port: 3000
  Env vars: ['NODE_ENV', 'DATABASE_URL']

[1/3] Creating sandbox...
  Sandbox ready: abc123xyz

[2/3] Setting up project...
  Found existing project: proj_123

[3/3] Deploying...
  Status: BUILDING
  Status: RUNNING

Deployment successful! (ID: dep_456)
  URL: https://my-webapp.novita.space
```

## Example Projects

This repository includes several example projects:

| Directory | Description | Stack |
|-----------|-------------|-------|
| `ecomm-with-sql/` | E-commerce store with SQL | Node.js, Vite, PostgreSQL |
| `snake-game-with-backend/` | Snake game with backend | Node.js, Vite, Express |
| `snake-game-static/` | Snake game (frontend only) | Static HTML/JS |

### Deploying an Example Project

1. Build a sandbox template:

```bash
cd ecomm-with-sql
novita-sandbox-cli template build -d ./novita.Dockerfile -n ecomm-with-sql
cd ..
```

2. Run the deployment:

```bash
python app.py --template ecomm-with-sql --project-name my-ecommerce --dockerfile ecomm-with-sql/Dockerfile
```

## Understanding the Deployment Script

### Key Components

**Template**: A pre-configured sandbox environment containing your source code and dependencies.

**Project**: A deployment target with a unique URL (e.g., `my-app.novita.space`).

**Dockerfile**: Defines how to build your application. Example for a Node.js app:

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install
COPY . .
RUN pnpm build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Environment Variables

There are two types of environment variables:

1. **Build-time variables** - Set in the Dockerfile with `ENV`. Required for frontend frameworks like Vite that inject variables during build:

```dockerfile
ENV VITE_API_URL=https://api.example.com
RUN pnpm build
```

2. **Runtime variables** - Passed via `environment_variables` in the deploy call. Available to your application at runtime:

```python
deployment = project.deploy(
    environment_variables={
        "DATABASE_URL": "postgresql://...",
    },
    ...
)
```

## Static Sites with Nginx

For static sites (HTML/CSS/JS only), use an Nginx-based Dockerfile:

```dockerfile
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY . /usr/share/nginx/html/
RUN chmod -R 755 /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Since Nginx listens on port 80, pass `--http-port 80`:

```bash
python app.py --template snake-game-static --project-name my-game --dockerfile snake-game-static/Dockerfile --http-port 80
```

## Troubleshooting

### Build Failed: "prepare context failed"

If you see this error, your sandbox may have a large `node_modules` directory. Add this before deploying:

```python
sandbox.commands.run(f"sudo rm -rf {ARTI_DIR}/node_modules")
```

### Deployment Stuck

Check if your application is listening on the correct port. The `http_port` parameter must match the port your app uses:

```python
deployment = project.deploy(
    http_port=3000,  # Must match your app's port
    ...
)
```

### Environment Variables Not Working

For Vite/React apps, `VITE_*` variables must be set at **build time** in the Dockerfile, not as runtime environment variables.

## Documentation

- [Novita Artifact Hosting SDK Documentation](./OFFICIAL.md)
- [Novita AI Platform](https://novita.ai)

## License

MIT
