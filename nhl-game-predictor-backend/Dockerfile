# ensure python version matches specified version in poetry
FROM python:3.11-slim

# env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# working directory will be app
WORKDIR /app

# get system dependencies
RUN apt-get update && apt-get install -y build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# get poetry dependencies files
COPY pyproject.toml poetry.lock ./

# install poetry and the specified dependencies within poetry
RUN pip install poetry
RUN poetry install --no-root

# copy application
COPY . .

# collect static files using poetry's run command
RUN poetry run python manage.py collectstatic --noinput

# handle any new migrations
RUN poetry run python manage.py makemigrations --noinput
RUN poetry run python manage.py migrate --noinput

# command to start the django application
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
