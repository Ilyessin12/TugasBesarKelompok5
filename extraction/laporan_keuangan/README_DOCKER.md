# Cara Menjalankan Proyek Ini dengan Docker

1. **Build Docker image**

   Jalankan perintah berikut di PowerShell pada folder project:

   ```powershell
   docker build -t lapkeu-scraper .
   ```

2. **Jalankan container dengan Docker Compose**

   ```powershell
   docker-compose up --build
   ```

   Atau untuk mode background (detached):

   ```powershell
   docker-compose up -d --build
   ```

3. **Cek hasil**

   - File hasil scraping akan tersimpan di `financial_reports.json` dan folder `downloads/`.
   - Untuk menghentikan container:
     ```powershell
     docker-compose down
     ```

4. **Konfigurasi**
   - Edit file `.env` untuk konfigurasi koneksi MongoDB dan parameter lain.

---

**Catatan:**

- Pastikan Docker Desktop sudah terinstall dan berjalan di Windows Anda.
- Jika ingin menjalankan manual tanpa compose:
  ```powershell
  docker run --env-file .env -v ${PWD}\downloads:/app/downloads -v ${PWD}\financial_reports.json:/app/financial_reports.json -v ${PWD}\emiten_list.json:/app/emiten_list.json lapkeu-scraper
  ```
