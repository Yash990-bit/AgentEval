# --- Build Stage ---
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (for caching)
COPY package*.json ./
RUN npm ci

# Copy application files
COPY . .

# Build production application (generates static files in /app/out)
RUN npm run build

# --- Runtime Stage ---
FROM nginx:alpine

# Install brotli modules for alpine nginx
RUN apk add --no-cache nginx-mod-http-brotli

# Configure Nginx main configuration file to load brotli modules
RUN sed -i '1s/^/load_module modules\/ngx_http_brotli_filter_module.so;\nload_module modules\/ngx_http_brotli_static_module.so;\n/' /etc/nginx/nginx.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from build stage
COPY --from=builder /app/out /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
