# ---- Deps (shared base: node + npm deps + source) ----
FROM node:22-alpine AS deps

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# ---- Dev target ----
FROM deps AS dev

EXPOSE 3000
CMD ["npm", "run", "dev"]

# ---- Builder target (runs via docker compose run on the runtime network) ----
FROM deps AS builder

CMD ["npm", "run", "build"]

# ---- Prod target (static file server — dist comes from a shared volume) ----
FROM caddy:2-alpine AS prod

EXPOSE 3000
CMD ["caddy", "file-server", "--root", "/srv", "--listen", ":3000"]
