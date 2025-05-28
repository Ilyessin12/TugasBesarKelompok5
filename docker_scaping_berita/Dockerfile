FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directories
RUN mkdir -p cache/news

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