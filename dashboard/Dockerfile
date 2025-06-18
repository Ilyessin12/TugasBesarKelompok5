# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install

# Copy source code and build
COPY . .
RUN pnpm build

# Stage 2: Create the production image
FROM node:18-alpine AS runner
WORKDIR /app

# Copy the standalone output from the builder stage
COPY --from=builder /app/.next/standalone ./
# Copy the public assets
COPY --from=builder /app/public ./public
# Copy the static assets
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# Run the standalone server
CMD ["node", "server.js"]