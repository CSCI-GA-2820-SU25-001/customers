FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY Pipfile Pipfile.lock ./

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --system

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "wsgi.py"]
