"""
YFinance Ingestion untuk import data saham ke MongoDB Atlas.
"""

import os
import json
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

from ..utils.common_utils import retry_operation

class YFinanceIngestion:
    """
    Class untuk ingestion data saham ke MongoDB Atlas.
    """
    
    def __init__(self):
        """
        Initialize YFinance ingestion.
        """
        load_dotenv()
        self.mongodb_uri = os.getenv("MONGODB_CONNECTION_STRING")
        self.mongodb_database = os.getenv("MONGODB_DATABASE_NAME")
        self.mongodb_collection = os.getenv("COLLECTION_YFINANCE_DATA")
        self.yfinance_output = os.getenv("YFINANCE_OUTPUT")
        self.logger = logging.getLogger(__name__)
        
        # Validasi koneksi MongoDB
        if not self.mongodb_uri:
            self.logger.error("MONGODB_CONNECTION_STRING tidak dikonfigurasi di file .env")
            raise ValueError("MONGODB_CONNECTION_STRING diperlukan untuk koneksi MongoDB")
        
        # Validasi database dan collection name
        if not isinstance(self.mongodb_database, str) or not self.mongodb_database:
            self.logger.error("MONGODB_DATABASE_NAME tidak valid, menggunakan default 'yfinance_db'")
            self.mongodb_database = "yfinance_db"
            
        if not isinstance(self.mongodb_collection, str) or not self.mongodb_collection:
            self.logger.error("MONGODB_COLLECTION_NAME tidak valid, menggunakan default 'stock_data'")
            self.mongodb_collection = "stock_data"
        
        # Log koneksi info
        self.logger.info(f"Menghubungkan ke MongoDB, database: {self.mongodb_database}, collection: {self.mongodb_collection}")
        
        # Inisialisasi koneksi MongoDB
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_database]
        self.collection = self.db[self.mongodb_collection]
    
    def __del__(self):
        """
        Destructor untuk menutup koneksi MongoDB.
        """
        if hasattr(self, 'client'):
            self.client.close()
    
    def load_stock_data(self) -> List[Dict[str, Any]]:
        """
        Load data saham dari file cache.
        
        Returns:
            List[Dict[str, Any]]: Daftar data saham
        """
        try:
            if not os.path.exists(self.yfinance_output):
                self.logger.error(f"File {self.yfinance_output} tidak ditemukan")
                return []
            
            with open(self.yfinance_output, 'r', encoding='utf-8') as f:
                stock_data = json.load(f)
            
            self.logger.info(f"Berhasil memuat {len(stock_data)} records dari {self.yfinance_output}")
            return stock_data
        except Exception as e:
            self.logger.error(f"Error saat memuat data saham: {str(e)}")
            return []
    
    def prepare_records(self, stock_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mempersiapkan records untuk dimasukkan ke MongoDB.
        
        Args:
            stock_data: Daftar data saham
            
        Returns:
            List[Dict[str, Any]]: Daftar records yang dipersiapkan
        """
        prepared_records = []
        
        for record in stock_data:
            # Parse tanggal dari format string
            date_str = record.get('Date')
            try:
                # Coba parse format tanggal
                date_parts = date_str.split(' - ')[0].split('/')
                date_obj = datetime(
                    year=int(date_parts[2]),
                    month=int(date_parts[1]),
                    day=int(date_parts[0])
                )
            except (ValueError, AttributeError, IndexError):
                # Jika gagal parse, gunakan waktu sekarang
                self.logger.warning(f"Gagal parse tanggal {date_str}, menggunakan waktu sekarang")
                date_obj = datetime.now()
            
            # Tambahkan field untuk tracking
            prepared_record = {
                **record,
                'date_obj': date_obj,
                'ingestion_timestamp': datetime.now(),
                'source': 'yfinance_scraper'
            }
            
            prepared_records.append(prepared_record)
        
        return prepared_records
    
    @retry_operation(max_retries=3, delay=5)
    def ingest_to_mongodb(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Ingesting data ke MongoDB dengan upsert (update jika sudah ada, insert jika belum).
        
        Args:
            records: Daftar records untuk dimasukkan
            
        Returns:
            Tuple[int, int]: (jumlah insert, jumlah update)
        """
        if not records:
            self.logger.warning("Tidak ada records untuk di-ingest")
            return (0, 0)
        
        # Buat operasi bulk upsert
        bulk_operations = []
        for record in records:
            # Gunakan kombinasi symbol dan date_obj sebagai unique identifier
            filter_query = {
                'symbol': record['symbol'],
                'Date': record['Date']
            }
            
            # Operasi upsert
            bulk_operations.append(
                UpdateOne(
                    filter_query,
                    {'$set': record},
                    upsert=True
                )
            )
        
        # Eksekusi bulk operations
        try:
            result = self.collection.bulk_write(bulk_operations)
            inserted = result.upserted_count
            updated = result.modified_count
            self.logger.info(f"Berhasil ingest {inserted} records baru dan update {updated} records")
            return (inserted, updated)
        except BulkWriteError as e:
            self.logger.error(f"Error saat melakukan bulk write: {str(e)}")
            raise
    
    def create_indexes(self):
        """
        Membuat indexes di MongoDB untuk optimasi query.
        """
        try:
            # Index untuk pencarian berdasarkan symbol
            self.collection.create_index("symbol")
            
            # Index untuk pencarian dan sorting berdasarkan tanggal
            self.collection.create_index("date_obj")
            
            # Compound index untuk pencarian unik berdasarkan symbol dan tanggal
            self.collection.create_index([("symbol", 1), ("date_obj", 1)], unique=True)
            
            self.logger.info("Berhasil membuat indexes di MongoDB")
        except Exception as e:
            self.logger.error(f"Error saat membuat indexes: {str(e)}")
    
    def ingest(self) -> Tuple[int, int]:
        """
        Proses lengkap untuk ingest data saham ke MongoDB.
        
        Returns:
            Tuple[int, int]: (jumlah insert, jumlah update)
        """
        # Load data saham
        stock_data = self.load_stock_data()
        if not stock_data:
            return (0, 0)
        
        # Persiapkan records
        prepared_records = self.prepare_records(stock_data)
        
        # Buat indexes jika belum ada
        self.create_indexes()
        
        # Ingest ke MongoDB
        return self.ingest_to_mongodb(prepared_records)


def main():
    """
    Main function untuk menjalankan YFinance ingestion.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inisialisasi dan jalankan ingestion
    try:
        ingestion = YFinanceIngestion()
        inserted, updated = ingestion.ingest()
        logging.info(f"YFinance ingestion completed. Inserted {inserted} and updated {updated} records.")
    except Exception as e:
        logging.error(f"Error running YFinance ingestion: {e}")


if __name__ == "__main__":
    main() 