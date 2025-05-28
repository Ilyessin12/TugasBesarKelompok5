# Docker untuk Scraping Berita Pasar Saham

Proyek ini berisi kontainer Docker untuk scraping berita saham dari website IQ Plus dan menyimpannya ke MongoDB Atlas.

## Struktur Proyek

```
docker_scraping_berita/
├── Dockerfile                    # Konfigurasi untuk container Python
├── docker-compose.yml           # Konfigurasi untuk multiple containers
├── requirements.txt             # Daftar semua dependencies Python
├── env.example                  # Template untuk environment variables
├── src/
│   ├── scrapers/                # Modul untuk scraping
│   │   ├── news_scraper.py      # Scraper untuk berita saham
│   │   └── emiten_list_*.json   # List kode emiten untuk di-scrape
│   │
│   ├── ingestion/               # Modul untuk ingestion ke MongoDB
│   │   └── news_ingestion.py    # Ingestion berita ke MongoDB
│   │
│   └── utils/                   # Fungsi-fungsi utility
│       ├── mongo_utils.py       # Utility untuk MongoDB
│       └── common_utils.py      # Utility umum
│
├── cache/                       # Folder untuk menyimpan data sementara
│   └── news/                    # Cache untuk data berita
│
└── scripts/
    └── main.py                  # Script utama
```

## Persyaratan

- Docker
- Docker Compose
- Koneksi internet untuk mengakses IQ Plus dan MongoDB Atlas
- Akun MongoDB Atlas

## Setup

1. Salin `env.example` ke `.env` dan isi variabel environment:

```bash
cp env.example .env
```

2. Edit `.env` dan isi kredensial MongoDB Anda:

```
MONGODB_CONNECTION_STRING=your_mongodb_atlas_connection_string
MONGODB_DATABASE_NAME=your_database_name
```

## Penggunaan

### Menjalankan keseluruhan pipeline

```bash
docker-compose up
```

### Menjalankan mode tertentu

```bash
# Untuk hanya menjalankan scraper
docker-compose run app python scripts/main.py --mode scrape

# Untuk hanya menjalankan ingestion
docker-compose run app python scripts/main.py --mode ingest
```

## Konfigurasi Docker

- Container Python: Menjalankan aplikasi scraping berita
- Container Selenium Chrome: Digunakan untuk scraping yang membutuhkan browser

## Menangani Data

Data akan disimpan:
1. Sementara di folder `cache/news/` selama proses berjalan
2. Secara permanen di MongoDB Atlas setelah ingestion

## Troubleshooting

- **Error koneksi MongoDB**: Pastikan connection string di `.env` benar dan MongoDB Atlas memperbolehkan koneksi dari IP Anda
- **Error scraping**: Cek log untuk detail error
- **Container crash**: Jalankan dengan mode verbose untuk melihat error:
  ```bash
  docker-compose up --verbose
  ``` 