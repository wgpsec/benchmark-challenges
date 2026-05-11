FROM python:3.11-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

COPY proxy.py .

EXPOSE 80

CMD ["python", "proxy.py"]
