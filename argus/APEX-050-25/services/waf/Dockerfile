FROM openresty/openresty:alpine
RUN apk add --no-cache curl
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY waf.lua /usr/local/openresty/nginx/conf/waf.lua
EXPOSE 80
CMD ["openresty", "-g", "daemon off;"]
