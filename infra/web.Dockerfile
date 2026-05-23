FROM node:22-alpine

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* ./
COPY web/package.json ./web/package.json
RUN pnpm install --filter mentriq360-web --frozen-lockfile

COPY web ./web

WORKDIR /app/web

EXPOSE 3000
