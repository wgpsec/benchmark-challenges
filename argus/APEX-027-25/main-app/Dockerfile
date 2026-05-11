FROM node:20-alpine

WORKDIR /app

ARG FLAG
ENV FLAG=${FLAG}

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

COPY src/ ./src/

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

USER nodejs

EXPOSE 3000

CMD ["node", "src/index.js"]
