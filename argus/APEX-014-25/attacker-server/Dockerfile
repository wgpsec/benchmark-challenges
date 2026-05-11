FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --omit=dev

COPY src/ ./src/

RUN chown -R node:node /app
USER node

EXPOSE 4014

CMD ["node", "src/index.js"]
