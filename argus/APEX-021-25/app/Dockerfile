FROM node:20-alpine

WORKDIR /app

# Install su-exec for privilege dropping
RUN apk add --no-cache su-exec

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "src/index.js"]
