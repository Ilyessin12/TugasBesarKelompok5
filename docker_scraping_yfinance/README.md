# YFinance Scraper

Aplikasi Docker sederhana untuk scraping data saham dari YFinance dengan periode 1 hari dan ingestion ke MongoDB Atlas.

## Deskripsi

Aplikasi ini menggunakan library YFinance untuk mengambil data saham dari Yahoo Finance API. Data yang diambil mencakup:
- Open price
- High price
- Low price
- Close price
- Volume
- Dividends
- Stock Splits

Data disimpan dalam format JSON di folder cache dan juga disimpan ke MongoDB Atlas untuk penyimpanan yang persisten.

## Struktur Proyek

```
docker_scraping_yfinance/
│
├── cache/                # Folder untuk menyimpan data hasil scraping
│
├── scripts/              # Script utama
│   ├── __init__.py
│   └── main.py           # Script utama untuk menjalankan scraper dan ingestion
│
├── src/                  # Source code
│   ├── __init__.py
│   │
│   ├── scrapers/         # Module scraper
│   │   ├── __init__.py
│   │   ├── yfinance_scraper.py
│   │   └── list_emiten.json # Daftar kode saham untuk scraping
│   │
│   ├── ingestion/        # Module ingestion untuk MongoDB
│   │   ├── __init__.py
│   │   └── yfinance_ingestion.py
│   │
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── common_utils.py
│
├── Dockerfile            # Dockerfile untuk build image
├── docker-compose.yml    # Docker Compose untuk menjalankan container
├── requirements.txt      # Daftar dependencies
└── env.example           # Contoh konfigurasi environment variables
```

## Penggunaan

### Konfigurasi

Salin file `env.example` menjadi `.env` dan sesuaikan konfigurasi:

```bash
cp env.example .env
```

Edit `.env` dengan setting yang sesuai:

```
# Output settings
YFINANCE_OUTPUT=/app/cache/yfinance/stock_data.json

# Stock settings
STOCK_PERIOD=1d
# Lokasi file list emiten, relatif terhadap container
EMITEN_LIST_FILE=/app/src/scrapers/list_emiten.json

# Logging settings
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Stock symbols to scrape (comma-separated)
# Leave empty to use emiten list from file
STOCK_SYMBOLS=BBRI.JK,BBCA.JK,BMRI.JK

# MongoDB settings
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE_NAME=yfinance_db
MONGODB_COLLECTION_NAME=stock_data
```

### Koneksi MongoDB Atlas

Untuk menghubungkan ke MongoDB Atlas:
1. Buat akun di [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Buat cluster baru atau gunakan yang sudah ada
3. Buat database user dengan username dan password
4. Dapatkan connection string dari dashboard MongoDB Atlas
5. Ganti `username`, `password` dan `cluster` pada MONGODB_CONNECTION_STRING di file `.env`

### Daftar Emiten

Aplikasi ini bisa mengambil daftar emiten saham dari:

1. **Environment Variable**: Menggunakan `STOCK_SYMBOLS` di file `.env`
2. **File JSON**: Jika `STOCK_SYMBOLS` kosong, aplikasi akan membaca file `list_emiten.json`

Format file `list_emiten.json`:
```json
[
    "BBRI.JK",
    "BBCA.JK",
    "BMRI.JK",
    "TLKM.JK",
    "ASII.JK"
]
```

### Menjalankan dengan Docker Compose

```bash
docker-compose up -d
```

### Mode Operasi

Aplikasi ini mendukung beberapa mode operasi:

```bash
# Jalankan scraper dan ingestion (default)
docker-compose run app python scripts/main.py --mode all

# Hanya jalankan scraper
docker-compose run app python scripts/main.py --mode scrape

# Hanya jalankan ingestion ke MongoDB
docker-compose run app python scripts/main.py --mode ingest
```

### Melihat Logs

```bash
docker-compose logs -f
```

### Menghentikan Container

```bash
docker-compose down
```

## Output

### File JSON

Data hasil scraping disimpan dalam format JSON di folder `cache/yfinance/`, dengan struktur:

```json
[
  {
    "Date": "01/01/2023 - 10:00",
    "Open": 4500.0,
    "High": 4550.0,
    "Low": 4480.0,
    "Close": 4520.0,
    "Volume": 1000000,
    "Dividends": 0.0,
    "Stock Splits": 0.0,
    "symbol": "BBRI.JK"
  },
  ...
]
```

### MongoDB

Data juga disimpan di MongoDB dengan field tambahan:
- `date_obj`: Field tanggal dalam format datetime MongoDB
- `ingestion_timestamp`: Waktu saat data dimasukkan ke MongoDB
- `source`: Sumber data (yfinance_scraper)

Indexes yang dibuat di MongoDB:
- Index pada `symbol` untuk pencarian cepat berdasarkan kode saham
- Index pada `date_obj` untuk sorting dan filtering berdasarkan tanggal
- Compound index pada `symbol` dan `date_obj` untuk menjamin keunikan data 