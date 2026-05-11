FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY html/ /usr/share/nginx/html/

# Rename _git to .git for the exposed git directory vulnerability
# (stored as _git in source to avoid git submodule issues)
RUN mv /usr/share/nginx/html/_git /usr/share/nginx/html/.git

# Create additional fake .git directories for realism
RUN mkdir -p /usr/share/nginx/html/.git/objects/pack \
    && mkdir -p /usr/share/nginx/html/.git/refs/heads

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
