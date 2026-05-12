FROM node:20-alpine

RUN apk --no-cache add curl
RUN npm config set registry https://registry.npmmirror.com

WORKDIR /app
COPY . .
RUN npm install 
RUN npm run build
EXPOSE 3000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["npm", "start"]