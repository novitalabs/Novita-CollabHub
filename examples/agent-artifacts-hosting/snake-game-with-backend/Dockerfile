# Stage 1: Build
FROM node:20-alpine AS builder
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
COPY patches ./patches
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
COPY patches ./patches
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate
RUN pnpm install --frozen-lockfile --prod
COPY --from=builder /app/dist ./dist
ENV NODE_ENV=production PORT=3000
EXPOSE 3000
CMD ["node", "dist/index.js"]
