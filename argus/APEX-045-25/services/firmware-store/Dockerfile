FROM nginx:alpine
RUN apk add --no-cache wget
COPY nginx.conf /etc/nginx/nginx.conf
COPY firmware/ /usr/share/nginx/html/firmware/
EXPOSE 8080
