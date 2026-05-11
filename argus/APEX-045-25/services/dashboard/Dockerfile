FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache wget
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production
COPY . .
EXPOSE 3045
CMD ["node", "server.js"]
