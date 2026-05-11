FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production
COPY server.js ./
EXPOSE 4000
CMD ["node", "server.js"]
