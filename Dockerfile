# Minimal Python image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project metadata first to leverage layer caching
COPY pyproject.toml ./

# Copy application code
COPY app ./app

# Install project and runtime dependencies declared in pyproject.toml
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Flask runs on 5455
EXPOSE 5455

# Default command: run Flask app
CMD ["python", "-m", "flask", "--app", "app.web", "run", "--host", "0.0.0.0", "--port", "5455"]
