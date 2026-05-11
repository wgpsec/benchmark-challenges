FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

COPY src/ ./src/

# Create storage directory
RUN mkdir -p /data/storage

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs && \
    chown -R nodejs:nodejs /data

USER nodejs

EXPOSE 4000

CMD ["node", "src/index.js"]
