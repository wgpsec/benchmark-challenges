FROM node:20-alpine

ARG FLAG=FLAG{default_flag_replace_me}
ENV FLAG=${FLAG}

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --only=production

# Copy source code
COPY src/ ./src/

# Create non-root user and set ownership
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3000

CMD ["node", "src/index.js"]
