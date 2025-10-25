FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

# Install OS-level build deps (keep minimal, then clean apt cache)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    gcc \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better caching, install Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create a non-root user and adjust ownership
RUN groupadd -r appgroup \
    && useradd -r -g appgroup -d /app -s /sbin/nologin appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

ENV FLASK_APP=app.py

# Run Flask on 0.0.0.0:8080
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
