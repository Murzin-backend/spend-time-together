FROM python:3.11-slim

WORKDIR /app

RUN mkdir static

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
ENV PATH="/opt/poetry/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]