FROM node:18-alpine
RUN apk add --no-cache curl
WORKDIR /app
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production
COPY server.js ./
EXPOSE 3001
CMD ["node", "server.js"]
