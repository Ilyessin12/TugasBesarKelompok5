FROM python:3.10-slim

WORKDIR /app

# Install ngrok and curl
RUN apt-get update && apt-get install -y wget unzip curl && \
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -O ngrok.tgz && \
    tar xvzf ngrok.tgz -C /usr/local/bin && \
    rm ngrok.tgz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make entrypoint script executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run our entrypoint script
CMD ["./entrypoint.sh"]