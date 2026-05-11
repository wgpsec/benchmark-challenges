FROM node:20-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm config set registry https://registry.npmmirror.com

RUN npm ci --omit=dev

# Copy application source
COPY src/ ./src/

# Set ownership
RUN chown -R node:node /app

# Switch to non-root user
USER node

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "src/index.js"]
