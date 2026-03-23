FROM node:22-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app

FROM base AS deps
COPY 15-minute-cities/package.json 15-minute-cities/pnpm-lock.yaml ./
RUN pnpm install --no-frozen-lockfile

FROM base AS builder
ARG MARTIN_URL=http://localhost:3001
ENV MARTIN_URL=$MARTIN_URL
COPY 15-minute-cities/ .
COPY --from=deps /app/node_modules ./node_modules
RUN pnpm build

FROM base AS runner
ENV NODE_ENV=production
COPY 15-minute-cities/package.json 15-minute-cities/pnpm-lock.yaml ./
RUN pnpm install --no-frozen-lockfile --prod
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.ts ./next.config.ts
EXPOSE 3000
CMD ["pnpm", "start"]
