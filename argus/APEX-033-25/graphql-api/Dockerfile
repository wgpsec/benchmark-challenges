FROM node:20-alpine

WORKDIR /app

ARG FLAG
ENV FLAG=${FLAG}

COPY package*.json ./
RUN npm install --omit=dev

COPY src/ ./src/

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Write flag to file for verification
RUN echo "${FLAG}" > /flag && \
    chmod 400 /flag && \
    chown nodejs:nodejs /flag

USER nodejs

EXPOSE 4000

CMD ["node", "src/index.js"]
