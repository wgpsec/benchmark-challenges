FROM node:20-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com

RUN npm install --production

COPY . .

# Create a secrets file that simulates sensitive data
RUN echo '{"api_key": "sk-internal-9f8e7d6c5b4a3210", "db_password": "super_secret_db_pass_2024"}' > /app/secrets.json

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Fix permissions for node user
RUN chown -R node:node /app

EXPOSE 3001

USER node

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "server.js"]
