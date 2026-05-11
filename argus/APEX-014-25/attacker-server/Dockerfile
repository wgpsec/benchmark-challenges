FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY src/ ./src/

RUN chown -R node:node /app
USER node

EXPOSE 4014

CMD ["node", "src/index.js"]
