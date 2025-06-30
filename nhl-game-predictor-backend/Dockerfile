# ensure python version matches specified version in poetry
FROM python:3.11-slim

# env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# working directory will be app
WORKDIR /app

# get system dependencies
RUN apt-get update && apt-get install -y build-essential postgresql-client && apt-get clean && rm -rf /var/lib/apt/lists/*

# get poetry dependencies files
COPY pyproject.toml poetry.lock ./

# install poetry and the specified dependencies within poetry
RUN pip install poetry
RUN poetry install --no-root

# copy application
COPY . .

# wait for postgres container to be ready before running entrypoint, which generates migrations
RUN chmod +x /app/wait-for-postgres.sh

# change permissions for entry point script and run
RUN chmod +x /app/scripts/bash/entrypoint.sh
ENTRYPOINT ["/app/scripts/bash/entrypoint.sh"]