FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY examples ./examples

CMD ["python", "-m", "src.demo"]
