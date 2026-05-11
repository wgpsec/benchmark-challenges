FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache wget
COPY package.json ./
RUN npm install --production
COPY server.js ./
EXPOSE 3052
CMD ["node", "server.js"]
