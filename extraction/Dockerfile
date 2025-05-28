FROM python:3.10-slim

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

# Set up working directory
WORKDIR /app

# Copy consolidated requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directories
# Adjusted to allow for potentially separate error log subdirectories
RUN mkdir -p cache/news_data cache/financial_reports cache/error_logs/news cache/error_logs/financial

# Copy source code and scripts from their respective subdirectories
COPY financial_report/src/ /app/src/financial_report/
COPY financial_report/scripts/ /app/scripts/financial_report/

COPY news/src/ /app/src/news/
COPY news/scripts/ /app/scripts/news/

# Copy yfinance directory
COPY yfinance/ /app/yfinance/

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app

# Create a non-root user
RUN useradd -m scraper
RUN chown -R scraper:scraper /app
USER scraper

# CMD is removed as it will be specified in docker-compose.yml for each service