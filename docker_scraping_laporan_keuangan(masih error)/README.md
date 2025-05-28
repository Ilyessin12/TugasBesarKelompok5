# Docker untuk Scraping Laporan Keuangan IDX

Proyek ini menyediakan solusi untuk mengotomatiskan scraping laporan keuangan XBRL dari website Bursa Efek Indonesia (IDX) menggunakan container Docker.

## Struktur Proyek

```
docker_scraping_laporan_keuangan/
├── Dockerfile                    # Konfigurasi untuk container Python
├── docker-compose.yml           # Konfigurasi untuk multiple containers
├── requirements.txt             # Daftar semua dependencies Python
├── env.example                  # Template untuk environment variables
├── src/
│   ├── scrapers/                # Modul untuk scraping
│   │   └── financial_scraper.py # Scraper untuk laporan keuangan
│   │
│   ├── ingestion/               # Modul untuk ingestion ke MongoDB
│   │   └── financial_ingestion.py
│   │
│   └── utils/                   # Fungsi-fungsi utility
│       └── common_utils.py
│
├── cache/                       # Folder untuk menyimpan data sementara
│   ├── financial_reports/
│   └── error_logs/
│
└── scripts/
    └── main.py                  # Script utama
```

## Persyaratan

- Docker
- Docker Compose
- Koneksi internet untuk mengakses website IDX

## Setup

1. Clone repositori ini

2. Salin `env.example` ke `.env` dan isi variabel environment:

```bash
cp env.example .env
```

3. Edit `.env` dan isi kredensial MongoDB Anda:

```
MONGODB_CONNECTION_STRING=your_mongodb_atlas_connection_string
MONGODB_DATABASE_NAME=your_database_name
```

## Penggunaan

### Menjalankan scraper laporan keuangan

```bash
docker-compose up
```

### Menjalankan mode atau tipe tertentu

```bash
# Untuk hanya menjalankan scraper
docker-compose run app python scripts/main.py --mode scrape

# Untuk hanya menjalankan ingestion
docker-compose run app python scripts/main.py --mode ingest
```

## Fitur

- **Scraper laporan keuangan**: Mengunduh laporan keuangan dalam format XBRL dari website IDX
- **Parser XBRL**: Mengubah data XBRL menjadi format JSON yang lebih mudah digunakan
- **Integrasi MongoDB**: Menyimpan data laporan keuangan ke MongoDB Atlas

## Troubleshooting

- **Error koneksi MongoDB**: Pastikan connection string di `.env` benar dan MongoDB memperbolehkan koneksi dari IP Anda
- **Error scraping**: Cek log di `cache/error_logs/` untuk detail error
- **Container crash**: Jalankan dengan mode verbose untuk melihat error:
  ```bash
  docker-compose up --verbose
  ``` 