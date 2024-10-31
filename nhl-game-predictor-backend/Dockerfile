# Use the official Python image from the Docker Hub with Python 3.11
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the poetry.lock and pyproject.toml files to the working directory
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry (without installing the current project)
RUN poetry install --no-root

# Copy the rest of your application code into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Start the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
