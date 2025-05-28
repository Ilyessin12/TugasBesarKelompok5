import os
import json
import time
import zipfile
import xml.etree.ElementTree as ET
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import logging

class IDXFinancialScraper:
    """
    Kelas untuk scraping laporan keuangan dari IDX
    """
    def __init__(self, base_download_dir=None, output_file=None, companies_file=None):
        """
        Inisialisasi scraper
        
        Parameters:
        -----------
        base_download_dir : str
            Direktori untuk menyimpan file yang diunduh
        output_file : str
            Path file JSON untuk menyimpan hasil scraping
        companies_file : str
            Path ke file daftar perusahaan
        """
        load_dotenv()  # Load environment variables
        
        self.current_dir = os.getcwd()
        
        # Gunakan nilai parameter atau ambil dari environment variable
        self.base_download_dir = base_download_dir or os.getenv("BASE_DOWNLOAD_DIR", "/app/cache/financial_reports/downloads")
        self.output_file = output_file or os.getenv("FINANCIAL_REPORTS_OUTPUT", "/app/cache/financial_reports/financial_reports.json")
        self.companies_file = companies_file or os.getenv("COMPANIES_LIST", "/app/emiten_list.json")
        
        # Siapkan path absolut
        self.base_dir = os.path.join(self.current_dir, self.base_download_dir) if not self.base_download_dir.startswith('/') else self.base_download_dir
        self.json_output_file = os.path.join(self.current_dir, self.output_file) if not self.output_file.startswith('/') else self.output_file
        
        # Buat direktori jika belum ada
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.json_output_file), exist_ok=True)
        
        self.existing_reports = []
        self.already_scraped_companies = set()
        self.driver = None
        
        # URL IDX Laporan Keuangan
        self.url = "https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan"
        
        # Daftar user agents untuk rotasi
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        ]
        
    def random_sleep(self, min_time=1.0, max_time=4.0):
        """
        Menunggu dengan durasi acak untuk mensimulasikan perilaku manusia
        
        Parameters:
        -----------
        min_time : float
            Durasi minimal (detik)
        max_time : float
            Durasi maksimal (detik)
        """
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)
        
    def random_scroll(self):
        """
        Melakukan scroll acak untuk mensimulasikan perilaku manusia
        """
        if not self.driver:
            return
            
        try:
            # Scroll ke posisi acak
            scroll_height = self.driver.execute_script("return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);")
            if scroll_height > 0:
                # Scroll dengan kecepatan acak
                target_scroll = random.randint(100, min(800, scroll_height))
                current_position = 0
                step_count = random.randint(5, 15)
                
                for _ in range(step_count):
                    current_position += target_scroll // step_count
                    self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                    self.random_sleep(0.1, 0.3)
        except Exception as e:
            print(f"Scroll error (dapat diabaikan): {e}")
            
    def move_mouse_randomly(self, element=None):
        """
        Menggerakkan mouse secara acak atau ke elemen tertentu
        
        Parameters:
        -----------
        element : WebElement, optional
            Elemen tujuan gerakan mouse
        """
        if not self.driver:
            return
            
        try:
            actions = ActionChains(self.driver)
            
            if element:
                # Gerakkan mouse ke elemen dengan jalur acak
                element_rect = element.rect
                element_x = element_rect['x'] + element_rect['width'] // 2
                element_y = element_rect['y'] + element_rect['height'] // 2
                
                # Hitung beberapa titik acak dalam jalur menuju elemen
                current_pos = (random.randint(100, 800), random.randint(100, 500))
                points = []
                
                for _ in range(random.randint(2, 5)):
                    # Titik antara posisi awal dan elemen
                    random_x = current_pos[0] + (element_x - current_pos[0]) * random.uniform(0.2, 0.8)
                    random_y = current_pos[1] + (element_y - current_pos[1]) * random.uniform(0.2, 0.8)
                    random_x += random.uniform(-50, 50)  # Tambahkan sedikit keacakan
                    random_y += random.uniform(-50, 50)
                    points.append((int(random_x), int(random_y)))
                
                # Gerakkan mouse melalui titik-titik acak
                for point in points:
                    actions.move_by_offset(point[0] - current_pos[0], point[1] - current_pos[1])
                    current_pos = point
                    actions.pause(random.uniform(0.1, 0.3))
                
                # Terakhir gerakkan ke elemen
                actions.move_to_element(element)
            else:
                # Gerakkan mouse ke posisi acak pada halaman
                for _ in range(random.randint(1, 3)):
                    actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
                    actions.pause(random.uniform(0.1, 0.3))
                    
            actions.perform()
        except Exception as e:
            print(f"Mouse movement error (dapat diabaikan): {e}")
                
    def load_existing_data(self):
        """
        Memuat data yang sudah ada dari file JSON
        """
        if os.path.exists(self.json_output_file):
            try:
                with open(self.json_output_file, 'r') as f:
                    self.existing_reports = json.load(f)
                    print(f"Loaded {len(self.existing_reports)} existing reports from {self.json_output_file}")
                    # Create a set of companies that have already been scraped
                    self.already_scraped_companies = {report['company'] for report in self.existing_reports}
                    print(f"Already scraped {len(self.already_scraped_companies)} companies")
            except json.JSONDecodeError:
                print(f"Error loading {self.json_output_file}, will create a new one")
                self.existing_reports = []
        return self.existing_reports, self.already_scraped_companies
                
    def setup_driver(self):
        """
        Setup WebDriver untuk scraping
        """
        options = webdriver.ChromeOptions()
        # Tambahkan argumen yang diperlukan untuk Docker
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        
        # Pilih User-Agent secara acak
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"user-agent={user_agent}")
        
        # Tambahkan header dan pengaturan tambahan untuk mengelabui anti-bot
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Set download preferences
        prefs = {
            "download.default_directory": self.base_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False
        }
        options.add_experimental_option("prefs", prefs)
            
        # Cek apakah berjalan di Docker (dengan Remote WebDriver)
        chrome_url = os.getenv("CHROME_URL")
        if chrome_url:
            print(f"Using remote WebDriver at {chrome_url}")
            self.driver = webdriver.Remote(
                command_executor=chrome_url,
                options=options
            )
        else:
            # Untuk lingkungan lokal/pengembangan
            print("Using local WebDriver")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        # Hapus tanda-tanda otomasi dengan JavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
        
    def load_companies(self, file_path=None):
        """
        Memuat daftar perusahaan dari file JSON
        
        Parameters:
        -----------
        file_path : str
            Path ke file emiten_list.json
            
        Returns:
        --------
        list : Daftar kode perusahaan yang perlu di-scrape
        """
        if file_path is None:
            file_path = self.companies_file
        
        try:
            # Coba gunakan file dari parameter atau atribut
            if os.path.exists(file_path):
                with open(file_path) as f:
                    data = json.load(f)
            else:
                # Coba gunakan path alternatif jika file tidak ditemukan
                alt_paths = [
                    "emiten_list.json",
                    "/app/src/scrapers/emiten_list.json",
                    os.path.join(os.path.dirname(__file__), "emiten_list.json")
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        with open(alt_path) as f:
                            data = json.load(f)
                        print(f"Loaded emiten list from {alt_path}")
                        break
                else:
                    # Jika semua path gagal, gunakan data default
                    print("❌ Could not find emiten_list.json, using default data")
                    data = ["AALI.JK", "BBCA.JK", "TLKM.JK"]  # Data default
                
            company_codes = [company_code.split(".")[0] for company_code in data]
            
            # Filter out companies that have already been scraped
            companies_to_scrape = [company for company in company_codes if company not in self.already_scraped_companies]
            print(f"Will scrape {len(companies_to_scrape)} remaining companies out of {len(company_codes)} total")
            return companies_to_scrape
        except Exception as e:
            print(f"❌ Error loading companies: {e}")
            # Kembalikan data minimal jika terjadi error
            return ["AALI", "BBCA", "TLKM"]
    
    def xml_to_dict(self, element):
        """
        Mengubah XML menjadi dictionary secara rekursif
        
        Parameters:
        -----------
        element : xml.etree.ElementTree.Element
            Elemen XML yang akan dikonversi
            
        Returns:
        --------
        dict : Dictionary hasil konversi XML
        """
        data = {}
        for child in element:
            tag = child.tag.split("}")[-1]  # Hapus namespace
            if len(child) > 0:
                data[tag] = self.xml_to_dict(child)
            else:
                data[tag] = child.text
        return data
    
    def parse_taxonomy(self, xsd_path):
        """
        Parsing file Taxonomy (.xsd) untuk mendapatkan definisi elemen
        
        Parameters:
        -----------
        xsd_path : str
            Path ke file taxonomy.xsd
            
        Returns:
        --------
        dict : Dictionary hasil parsing taxonomy
        """
        if not os.path.exists(xsd_path):
            print(f"❌ Taxonomy file {xsd_path} not found!")
            return {}

        try:
            tree = ET.parse(xsd_path)
            root = tree.getroot()
            taxonomy_dict = {}

            for elem in root.iter():
                tag = elem.tag.split("}")[-1]  # Hapus namespace
                if "name" in elem.attrib:
                    taxonomy_dict[elem.attrib["name"]] = {
                        "type": elem.attrib.get("type", "unknown"),
                        "documentation": elem.attrib.get("documentation", "No description")
                    }

            print(f"✅ Parsed taxonomy {xsd_path}")
            return taxonomy_dict

        except Exception as e:
            print(f"❌ Error parsing taxonomy: {e}")
            return {}
    
    def scrape_company(self, company):
        """
        Scrape laporan keuangan untuk satu perusahaan
        
        Parameters:
        -----------
        company : str
            Kode perusahaan
        
        Returns:
        --------
        dict or None : Data laporan keuangan atau None jika gagal
        """
        try:
            wait_time = random.randint(10, 20)  # Waktu tunggu acak untuk mengelabui deteksi
            
            print(f"Navigating to {self.url}")
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, wait_time)
            
            # Tunggu dengan durasi acak untuk memberi kesan natural
            self.random_sleep(3, 6)
            
            # Lakukan scroll acak di halaman
            self.random_scroll()
            
            # Debug informasi
            print(f"Page title: {self.driver.title}")
            
            # Tunggu halaman dimuat sepenuhnya dengan perilaku manusia
            self.random_sleep(2, 4)
            
            # Tunggu sampai input perusahaan muncul
            try:
                print("Waiting for company search input...")
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.vs__search")))
                
                # Berikan sedikit penundaan untuk mensimulasikan perilaku manusia
                self.random_sleep(1, 2.5)
                
                # Gerakkan mouse ke kotak pencarian
                self.move_mouse_randomly(search_box)
                
                print(f"Clearing and typing company code: {company}")
                search_box.clear()
                self.driver.execute_script("arguments[0].value = '';", search_box)  # Clear lagi dengan JS
                
                # Ketik kode perusahaan karakter demi karakter dengan kecepatan acak
                for char in company:
                    search_box.send_keys(char)
                    self.random_sleep(0.1, 0.3)  # Penundaan ketik antar karakter
                
                # Tunggu dropdown muncul dengan durasi acak
                self.random_sleep(1.5, 3)
                
                # Coba klik dengan JavaScript untuk hasil pertama
                print("Looking for company dropdown option...")
                first_suggestion = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".vs__dropdown-option")))
                
                # Gerakkan mouse dengan jalur acak ke saran pertama
                self.move_mouse_randomly(first_suggestion)
                
                print("Clicking first company suggestion...")
                # Kadang klik dengan JavaScript, kadang klik langsung
                if random.choice([True, False]):
                    self.driver.execute_script("arguments[0].click();", first_suggestion)
                else:
                    first_suggestion.click()
                
                # Tunggu setelah klik dengan durasi acak
                self.random_sleep(2, 4)
                
                print("Applying filters...")
                # Klik filter dengan JavaScript
                try:
                    # Coba klik tombol filter utama dulu jika ada
                    filter_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-filter-input")
                    
                    # Gerakkan mouse ke tombol filter
                    self.move_mouse_randomly(filter_button)
                    
                    # Klik menggunakan JavaScript atau klik biasa secara acak
                    if random.choice([True, False]):
                        self.driver.execute_script("arguments[0].click();", filter_button)
                    else:
                        filter_button.click()
                        
                    self.random_sleep(1, 2)
                except:
                    pass  # Lanjutkan jika tidak ada tombol filter
                
                # Siapkan daftar filter yang perlu diklik
                filter_elements = [
                    {"id": "FinancialStatement", "name": "Financial Statement"},
                    {"id": "TypeSaham", "name": "Stock Type"},
                    {"id": "year1", "name": "Year 2024"},
                    {"id": "period3", "name": "Annual"}
                ]
                
                # Acak urutan filter untuk membuat pola yang lebih manusiawi
                random.shuffle(filter_elements)
                
                # Klik semua filter yang diperlukan dengan JavaScript dan tunggu di antara klik
                for filter_elem in filter_elements:
                    try:
                        element = wait.until(EC.presence_of_element_located((By.ID, filter_elem["id"])))
                        print(f"Clicking filter: {filter_elem['name']}")
                        
                        # Gerakkan mouse ke elemen filter
                        self.move_mouse_randomly(element)
                        
                        # Klik dengan durasi acak
                        self.random_sleep(0.5, 1.5)
                        
                        # Klik menggunakan JavaScript atau klik biasa secara acak
                        if random.choice([True, False]):
                            self.driver.execute_script("arguments[0].click();", element)
                        else:
                            element.click()
                            
                        # Tunggu dengan durasi acak antar klik filter
                        self.random_sleep(0.7, 1.8)
                    except Exception as filter_error:
                        print(f"Warning: Filter {filter_elem['name']} not clickable: {filter_error}")
                
                # Lakukan scroll acak lagi
                self.random_scroll()
                
                # Klik tombol Terapkan
                print("Clicking Apply button...")
                apply_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Terapkan')]")))
                
                # Gerakkan mouse ke tombol Terapkan
                self.move_mouse_randomly(apply_button)
                
                # Tunggu sebentar sebelum klik
                self.random_sleep(0.8, 2)
                
                # Klik menggunakan JavaScript atau klik biasa secara acak
                if random.choice([True, False]):
                    self.driver.execute_script("arguments[0].click();", apply_button)
                else:
                    apply_button.click()
                
                # Tunggu tabel dimuat dengan durasi acak
                self.random_sleep(3, 7)
                
                # Lakukan scroll acak di halaman hasil
                self.random_scroll()
                
                # Tunggu tabel laporan muncul
                print("Waiting for table to appear...")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                
                # Debug: cetak jumlah baris tabel
                rows = self.driver.find_elements(By.TAG_NAME, "tr")
                print(f"Found {len(rows)} rows in table")
                
                # Cari dan download file "instance.zip"
                download_found = False
                print("Looking for instance.zip link...")
                
                for row in rows:
                    try:
                        # Debug: cetak teks baris untuk melihat konten
                        row_text = row.text
                        if "instance.zip" in row_text:
                            print(f"Found row with instance.zip: {row_text}")
                            link_element = row.find_element(By.TAG_NAME, "a")
                            href = link_element.get_attribute("href")
                            print(f"Link URL: {href}")
                            
                            # Scroll dengan perilaku manusia untuk melihat link
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                link_element
                            )
                            
                            # Tunggu scroll selesai
                            self.random_sleep(1, 3)
                            
                            # Gerakkan mouse ke link download
                            self.move_mouse_randomly(link_element)
                            
                            # Tunggu sebentar sebelum klik
                            self.random_sleep(0.5, 1.5)
                            
                            # Klik link download (kadang dengan JavaScript, kadang klik biasa)
                            if random.choice([True, False]):
                                self.driver.execute_script("arguments[0].click();", link_element)
                            else:
                                link_element.click()
                                
                            print(f"✅ Download started for {company}")
                            download_found = True
                            break
                    except Exception as row_e:
                        print(f"Error processing row: {row_e}")
                        continue
                if not download_found:
                    print(f"⚠️ No instance.zip found for {company}")
                    return None
                
                # Tunggu unduhan selesai dengan waktu acak
                download_wait = random.randint(10, 20)
                print(f"Waiting {download_wait} seconds for download to complete...")
                time.sleep(download_wait)
                
                # === Ekstraksi File ZIP ===
                zip_path = os.path.join(self.base_dir, "instance.zip")
                extract_dir = os.path.join(self.base_dir, company)
                os.makedirs(extract_dir, exist_ok=True)
                
                if os.path.exists(zip_path):
                    print(f"File instance.zip found at {zip_path}, size: {os.path.getsize(zip_path)} bytes")
                    try:
                        with zipfile.ZipFile(zip_path, "r") as zip_ref:
                            zip_ref.extractall(extract_dir)
                        print(f"✅ Extracted {company} instance.zip")
                    except zipfile.BadZipFile:
                        print(f"❌ Error: {company} instance.zip is not a valid ZIP file")
                        return None
                    finally:
                        os.remove(zip_path)  # Hapus ZIP setelah ekstraksi
                else:
                    print(f"❌ Error: ZIP file was not downloaded for {company}")
                    return None
                
                # === Parsing Taxonomy ===
                xsd_path = os.path.join(extract_dir, "taxonomy.xsd")
                taxonomy_dict = self.parse_taxonomy(xsd_path)
                
                # === Konversi XBRL ke JSON & Simpan ke Dictionary ===
                xbrl_path = os.path.join(extract_dir, "instance.xbrl")
                
                if os.path.exists(xbrl_path):
                    try:
                        tree = ET.parse(xbrl_path)
                        root = tree.getroot()
                        xbrl_dict = self.xml_to_dict(root)
                        
                        # Gabungkan XBRL dengan Taxonomy
                        enriched_data = {
                            "company": company,
                            "timestamp": datetime.now().isoformat(),
                            "taxonomy": taxonomy_dict,
                            "xbrl_data": xbrl_dict
                        }
                        
                        print(f"✅ {company} data processed successfully!")
                        return enriched_data
                    
                    except Exception as e:
                        print(f"❌ Error processing {company}.xbrl: {e}")
                        return None
                else:
                    print(f"❌ instance.xbrl not found for {company}")
                    return None
                    
            except Exception as search_error:
                print(f"❌ Error during search and download: {search_error}")
                return None
            
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")
            if self.driver:
                print(f"Current URL: {self.driver.current_url}")
                # Take screenshot to diagnose issues
                try:
                    screenshot_path = os.path.join(self.base_dir, f"{company}_error.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")
                except:
                    pass
            return None
    
    def save_to_json(self, all_financial_reports):
        """
        Simpan laporan keuangan ke file JSON
        
        Parameters:
        -----------
        all_financial_reports : list
            Daftar laporan keuangan untuk disimpan
        """
        with open(self.json_output_file, 'w') as f:
            json.dump(all_financial_reports, f, indent=2)
        print(f"📂 Saved {len(all_financial_reports)} financial reports to {self.json_output_file}")
    
    def close(self):
        """
        Tutup WebDriver
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("Browser closed.")
    
    def run(self, companies_file=None):
        """
        Jalankan proses scraping secara keseluruhan
        
        Parameters:
        -----------
        companies_file : str
            Path ke file daftar perusahaan (emiten_list.json)
            
        Returns:
        --------
        list : Daftar laporan keuangan yang berhasil diunduh
        """
        try:
            # Setup
            self.load_existing_data()
            self.setup_driver()
            
            # Gunakan parameter atau atribut class
            file_path_to_use = companies_file or self.companies_file
            companies_to_scrape = self.load_companies(file_path_to_use)
            
            # Inisialisasi dengan data yang sudah ada
            all_financial_reports = self.existing_reports
            
            # Acak urutan perusahaan untuk mengelabui deteksi pola
            if random.choice([True, False]):
                random.shuffle(companies_to_scrape)
                print("Randomized company processing order")
            
            # Proses scraping
            for i, company in enumerate(companies_to_scrape):
                print(f"\n[{i+1}/{len(companies_to_scrape)}] Processing {company}...")
                report_data = self.scrape_company(company)
                
                if report_data:
                    all_financial_reports.append(report_data)
                    
                # Simpan progress setiap 5 perusahaan atau dengan pola acak
                if len(all_financial_reports) % 5 == 0 or random.random() < 0.2:
                    self.save_to_json(all_financial_reports)
                    print(f"Interim save: {len(all_financial_reports)} reports saved")
                
                # Tunggu dengan durasi acak antara perusahaan untuk menghindari deteksi
                if i < len(companies_to_scrape) - 1:
                    wait_time = random.uniform(3, 10)
                    print(f"Waiting {wait_time:.2f} seconds before next company...")
                    time.sleep(wait_time)
            
            # Simpan hasil akhir
            self.save_to_json(all_financial_reports)
            return all_financial_reports
            
        except Exception as e:
            print(f"❌ Error during scraping process: {e}")
            # Simpan progress jika terjadi error
            if 'all_financial_reports' in locals():
                self.save_to_json(all_financial_reports)
            return []
        finally:
            self.close()

    def scrape_financial_reports(self):
        """
        Metode kompatibilitas dengan FinancialReportScraper dari main.py
        
        Returns:
        --------
        list : Daftar laporan keuangan yang berhasil diunduh
        """
        return self.run()

# Alias class IDXFinancialScraper sebagai FinancialReportScraper untuk kompatibilitas
FinancialReportScraper = IDXFinancialScraper

def main():
    """
    Fungsi utama untuk menjalankan scraper
    """
    # Load environment variables
    load_dotenv()
    
    # Konfigurasi logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run scraper
    scraper = FinancialReportScraper()
    reports = scraper.scrape_financial_reports()

    return reports

if __name__ == "__main__":
    main() 