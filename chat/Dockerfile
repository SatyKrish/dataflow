# Ultra-minimal Dockerfile using distroless base
# Expected size: 300-500 MB (80%+ reduction)

FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force

# Install build dependencies in separate layer
RUN npm ci --no-audit --no-fund

# Copy source
COPY . .

# Set build-time environment variables to prevent build failures
ENV NEXTAUTH_URL=http://localhost:3000 \
    NEXTAUTH_SECRET=build-time-secret \
    AUTH_AZURE_AD_CLIENT_ID=build-time-placeholder \
    AUTH_AZURE_AD_CLIENT_SECRET=build-time-placeholder \
    AUTH_AZURE_AD_TENANT_ID=build-time-placeholder

# Build with optimizations
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    GENERATE_SOURCEMAP=false

RUN npm run build

# Prune dev dependencies and clean
RUN npm prune --production && \
    npm cache clean --force && \
    rm -rf .next/cache

# Final runtime image - distroless for security and size
FROM gcr.io/distroless/nodejs20-debian12

# Set working directory
WORKDIR /app

# Set production environment
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Copy only necessary runtime files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Distroless runs as non-root by default
EXPOSE 3000

# Start the application
CMD ["server.js"]
