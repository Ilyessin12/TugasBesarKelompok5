# Gunakan image Python versi terbaru
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Salin file requirements dan install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file ke dalam container
COPY . .

# Perintah default saat container dijalankan
CMD ["python", "tugas1yfinance.py"]
