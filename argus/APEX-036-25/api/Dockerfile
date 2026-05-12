FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache su-exec

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

COPY src/ ./src/

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "src/index.js"]
