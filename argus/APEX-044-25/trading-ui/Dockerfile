FROM node:20-alpine

RUN apk add --no-cache curl

WORKDIR /app

COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production

COPY src/ ./src/

ENV NODE_ENV=production
EXPOSE 3044

CMD ["node", "src/index.js"]
