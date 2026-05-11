FROM node:16-alpine

RUN apk --no-cache add curl
RUN npm config set registry https://registry.npmmirror.com
WORKDIR /app
COPY . .
RUN npm install 
EXPOSE 8333
CMD [ "npm", "start" ]
