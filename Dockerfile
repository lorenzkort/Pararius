# Use slim Python image as base
FROM python:3.11-slim-bullseye

# Create and set working directory
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install chromium and chromium-driver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    # Required dependencies
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies (if any)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Command to run your Python app
CMD ["python", "app.py"]
