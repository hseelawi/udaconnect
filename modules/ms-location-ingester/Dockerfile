FROM python:3.11.6-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

ENV GRPC_SERVER_PORT=50051

EXPOSE $GRPC_SERVER_PORT

CMD ["python", "geolocation_server.py"]
