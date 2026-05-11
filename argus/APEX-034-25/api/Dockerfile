FROM node:20-alpine

WORKDIR /app

COPY package.json .
RUN npm install --production

COPY src/ ./src/

ARG FLAG="FLAG{c0up0n_st4ck1ng_pr1c3_m4n1pul4t10n}"
ENV FLAG=${FLAG}

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "src/app.js"]
