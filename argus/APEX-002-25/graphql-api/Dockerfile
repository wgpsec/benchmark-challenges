FROM node:20-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./
RUN npm install --omit=dev

# Copy source
COPY src/ ./src/

# Flag injection
ARG FLAG
ENV APP_FLAG=${FLAG}

EXPOSE 4000

CMD ["node", "src/index.js"]
