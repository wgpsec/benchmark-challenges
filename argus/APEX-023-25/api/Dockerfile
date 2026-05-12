FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

# Copy application code
COPY src/ ./src/

# Install su-exec for privilege dropping
RUN apk add --no-cache su-exec

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "src/index.js"]
