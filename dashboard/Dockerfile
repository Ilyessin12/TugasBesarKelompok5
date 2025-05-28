# Stage 1: Build
FROM node:18-alpine AS builder

# Set direktori kerja
WORKDIR /app

# Salin package.json dan package-lock.json
COPY package*.json ./

# Instal dependensi
RUN npm install

# Salin semua file proyek
COPY . .

# Build aplikasi Next.js
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine AS runner

# Set direktori kerja
WORKDIR /app

# Salin hasil build dari stage builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# (Opsional) Jika Anda ingin menyertakan node_modules untuk dependensi runtime
# COPY --from=builder /app/node_modules ./node_modules


# Expose port
EXPOSE 3000

# Jalankan aplikasi
CMD ["npm", "start"]