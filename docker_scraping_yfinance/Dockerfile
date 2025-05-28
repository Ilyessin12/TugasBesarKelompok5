FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directories
RUN mkdir -p cache/yfinance

# Copy source code
COPY src/ /app/src/
COPY scripts/ /app/scripts/

# Set environment variables
ENV PYTHONPATH=/app

# Create a non-root user
RUN useradd -m scraper
RUN chown -R scraper:scraper /app
USER scraper

# Run the application
CMD ["python", "scripts/main.py"] 