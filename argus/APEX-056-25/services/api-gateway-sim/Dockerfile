FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache wget
COPY package.json ./
RUN npm install --production
COPY server.js ./
EXPOSE 3056
CMD ["node", "server.js"]
