FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY n8nManager/ ./n8nManager/
COPY config.json .

RUN pip install --no-cache-dir .

EXPOSE 8100

CMD ["n8n-manager", "serve", "--port", "8100"]
