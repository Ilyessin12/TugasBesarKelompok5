"""
YFinance scraper untuk mengambil data saham dengan period 1 day.
"""

import os
import json
import logging
from typing import List, Dict, Any
import yfinance as yf
from dotenv import load_dotenv

from ..utils.common_utils import save_to_json, retry_operation, ensure_dir

class YFinanceScraper:
    """
    Class untuk scraping data saham menggunakan yfinance.
    """
    
    def __init__(self):
        """
        Initialize YFinance scraper.
        """
        load_dotenv()
        self.yfinance_output = os.getenv("YFINANCE_OUTPUT", "/app/cache/yfinance/stock_data.json")
        self.stock_period = os.getenv("STOCK_PERIOD", "1d")
        self.stock_symbols = os.getenv("STOCK_SYMBOLS", "")
        self.emiten_list_file = os.getenv("EMITEN_LIST_FILE", "/app/src/scrapers/list_emiten.json")
        self.logger = logging.getLogger(__name__)
    
    @retry_operation(max_retries=3, delay=5)
    def scrape_stock_data(self, stock_symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape stock data untuk daftar saham.
        
        Args:
            stock_symbols: Daftar kode saham
            
        Returns:
            List[Dict[str, Any]]: Daftar data saham
        """
        # List untuk menyimpan semua data
        all_data = []
        
        # Proses setiap saham
        for symbol in stock_symbols:
            # Pastikan kode saham memiliki akhiran .JK
            if not symbol.endswith('.JK') and not '.' in symbol:
                symbol = f"{symbol}.JK"
                
            self.logger.info(f"Memproses {symbol}...")
            try:
                # Ambil data saham
                stock = yf.Ticker(symbol)
                data = stock.history(period=self.stock_period)
                    
                # Lewati jika tidak ada data
                if data.empty:
                    self.logger.warning(f"Tidak ada data untuk {symbol}")
                    continue
                
                # Reset index untuk menjadikan Date sebagai kolom reguler
                data.reset_index(inplace=True)
                
                # Konversi Date ke format string
                data["Date"] = data["Date"].apply(lambda x: x.strftime("%d/%m/%Y - %H:%M"))
                
                # Konversi DataFrame ke list dictionaries
                records = json.loads(data.to_json(orient="records"))
                
                # Tambahkan informasi saham ke setiap record
                for record in records:
                    record["symbol"] = symbol
                    
                # Tambahkan records ke list utama
                all_data.extend(records)
                
                self.logger.info(f"Menambahkan {len(records)} records untuk {symbol}")
            except Exception as e:
                self.logger.error(f"Error saat memproses {symbol}: {str(e)}")
        
        # Simpan semua data ke file JSON
        save_to_json(all_data, self.yfinance_output)
        self.logger.info(f"Berhasil menyimpan {len(all_data)} records ke {self.yfinance_output}")
        
        return all_data
    
    def load_emiten_list_from_file(self) -> List[str]:
        """
        Load daftar emiten dari file JSON.
        
        Returns:
            List[str]: Daftar kode saham
        """
        try:
            # Cek apakah file ada
            if not os.path.exists(self.emiten_list_file):
                self.logger.warning(f"File {self.emiten_list_file} tidak ditemukan.")
                return []
                
            # Baca file JSON
            with open(self.emiten_list_file, 'r', encoding='utf-8') as f:
                emiten_list = json.load(f)
                
            self.logger.info(f"Berhasil memuat {len(emiten_list)} emiten dari file {self.emiten_list_file}")
            return emiten_list
        except Exception as e:
            self.logger.error(f"Error saat memuat daftar emiten dari file: {str(e)}")
            return []
    
    def create_default_emiten_list(self) -> List[str]:
        """
        Buat daftar emiten default dan simpan ke file.
        
        Returns:
            List[str]: Daftar kode saham default
        """
        default_list = ["BBRI.JK", "BBCA.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]
        
        # Pastikan direktori ada
        ensure_dir(os.path.dirname(self.emiten_list_file))
        
        # Simpan ke file
        try:
            with open(self.emiten_list_file, 'w', encoding='utf-8') as f:
                json.dump(default_list, f, indent=4)
                
            self.logger.info(f"Berhasil membuat file daftar emiten default di {self.emiten_list_file}")
        except Exception as e:
            self.logger.error(f"Error saat membuat file daftar emiten default: {str(e)}")
        
        return default_list
    
    def parse_stock_symbols(self) -> List[str]:
        """
        Parse daftar saham dari environment variable atau file.
        
        Returns:
            List[str]: Daftar kode saham
        """
        # Jika STOCK_SYMBOLS diisi, gunakan itu
        if self.stock_symbols:
            # Split daftar saham berdasarkan koma
            stock_list = [s.strip() for s in self.stock_symbols.split(",") if s.strip()]
            self.logger.info(f"Menggunakan {len(stock_list)} saham dari environment variable")
            return stock_list
        
        # Jika tidak, coba load dari file
        emiten_list = self.load_emiten_list_from_file()
        
        # Jika file tidak ada atau kosong, buat default
        if not emiten_list:
            self.logger.warning("File daftar emiten kosong atau tidak ada. Membuat daftar default.")
            return self.create_default_emiten_list()
            
        return emiten_list
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Jalankan YFinance scraper.
        
        Returns:
            List[Dict[str, Any]]: Daftar data saham
        """
        # Parse daftar saham
        stock_symbols = self.parse_stock_symbols()
        
        # Scrape data saham
        return self.scrape_stock_data(stock_symbols)


def main():
    """
    Main function untuk menjalankan YFinance scraper.
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    # Buat direktori cache
    output_path = os.getenv("YFINANCE_OUTPUT", "/app/cache/yfinance/stock_data.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Inisialisasi dan jalankan scraper
    scraper = YFinanceScraper()
    scraper.run()


if __name__ == "__main__":
    main() 