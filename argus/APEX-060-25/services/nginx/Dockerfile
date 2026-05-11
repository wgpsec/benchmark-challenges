FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY package.json ./
RUN npm install --production
COPY server.js ./
EXPOSE 3060
CMD ["node", "server.js"]
