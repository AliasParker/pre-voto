# ---- Dev target ----
FROM node:22-alpine AS dev

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]

# ---- Build ----
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Prod target ----
FROM caddy:2-alpine AS prod

COPY --from=build /app/dist /srv
EXPOSE 3000

CMD ["caddy", "file-server", "--root", "/srv", "--listen", ":3000"]
