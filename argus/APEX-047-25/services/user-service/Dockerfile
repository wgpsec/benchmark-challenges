FROM node:18-alpine
RUN apk --no-cache add curl wget
WORKDIR /app
COPY package.json ./
RUN npm install --production
COPY . .
EXPOSE 3001
CMD ["node", "server.js"]
