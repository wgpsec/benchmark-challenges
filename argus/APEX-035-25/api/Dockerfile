FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production

# Copy application
COPY src/ ./src/
COPY public/ ./public/

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000

CMD ["node", "src/index.js"]
