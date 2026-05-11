FROM node:20-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy source code with proper ownership
COPY --chown=nodejs:nodejs src/ ./src/

USER nodejs

EXPOSE 3000

# VULNERABLE: Use --insecure-http-parser to accept requests with both CL and TE
# This is required for CL.TE request smuggling to work
CMD ["node", "--insecure-http-parser", "src/index.js"]
