FROM node:18-alpine
RUN apk add --no-cache curl
WORKDIR /app
COPY package.json ./
RUN npm install --production
COPY server.js ./
EXPOSE 3054
CMD ["node", "server.js"]
