FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY aiscm/ aiscm/
COPY config/ config/

RUN pip install --no-cache-dir .

EXPOSE 8150

CMD ["aiscm", "dashboard", "--port", "8150"]
