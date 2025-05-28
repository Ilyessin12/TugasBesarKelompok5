import os
import json
import logging
from dotenv import load_dotenv
import pymongo
from datetime import datetime
import time
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def summarize_text_with_gemini(text, max_length=150, retries=3):
    for attempt in range(retries):
        try:
            # Configure Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            
            # Initialize model
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Truncate to 500,000 characters (Gemini’s token limit is ~128,000 tokens)
            text = text[:500000]
            
            # Create prompt for concise summarization
            prompt = f"Ringkas teks berikut dalam satu paragraf singkat (maks {max_length} kata) dalam bahasa Indonesia:\n\n{text}"
            
            # Generate summary
            response = model.generate_content(prompt)
            summary = response.text.strip()
            
            logger.info("Summarization completed for text: %s", text[:50])
            return summary
        
        except Exception as e:
            if "429" in str(e):
                logger.warning("Rate limit exceeded on attempt %d/%d, retrying in %d seconds", 
                              attempt + 1, retries, 20 * (attempt + 1))
                time.sleep(20 * (attempt + 1))
            else:
                logger.error("Gemini API error on attempt %d/%d: %s", attempt + 1, retries, str(e))
                if attempt + 1 == retries:
                    return "Error: Could not summarize article after retries"
                time.sleep(2)
    return "Error: Could not summarize article after retries"

def save_checkpoint(results, part, batch_num):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(current_dir, 'Batch')
        checkpoint_filename = os.path.join(base_dir, f"checkpoint_pt{part}_batch{batch_num}.json")
        os.makedirs(base_dir, exist_ok=True)
        with open(checkpoint_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info("Checkpoint %d saved to %s", batch_num, checkpoint_filename)
        return checkpoint_filename
    except Exception as e:
        logger.error("Error saving checkpoint: %s", str(e))
        raise

def process_news_data_from_mongo(checkpoint_interval=100):
    client = None
    try:
        # Connect to MongoDB
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("MONGODB_CONNECTION_STRING not found in environment")
        client = pymongo.MongoClient(connection_string)
        db = client["Big_Data_kel_5"]
        collection = db["Docker_Scraping_Berita"]
        output_collection = db["Docker_Transformasi_Berita"]
        
        logger.info("Connecting to MongoDB: %s, Collection: %s", "Big_Data_kel_5", "Data_Berita")
        
        # Verify database and collection
        if "Big_Data_kel_5" not in client.list_database_names():
            raise ValueError("Database 'Big_Data_kel_5' not found")
        if "Data_Berita" not in db.list_collection_names():
            raise ValueError("Collection 'Data_Berita' not found")
        
        # Fetch news data
        news_data = list(collection.find())
        logger.info("Processing %d news items from MongoDB", len(news_data))
        
        if not news_data:
            logger.warning("No news items found in Data_Berita")
            return
        
        processed_data = []
        batch_num = 1
        skipped_items = 0
        for idx, news_item in enumerate(news_data, 1):
            content = news_item.get("content") or news_item.get("Content")
            judul = news_item.get("Judul") or news_item.get("Title")
            
            if content and judul:
                full_text = f"{judul} {content}"
                logger.debug("Processing item %d: Judul=%s, Content length=%d", idx, judul[:50], len(content))
                summary = summarize_text_with_gemini(full_text)
                news_item["Ringkasan"] = summary
                news_item["uploaded_at"] = datetime.now()
                processed_data.append(news_item)
            else:
                logger.warning("Skipping item %d: Missing or empty content/Judul (content=%s, Judul=%s)", 
                              idx, str(content)[:50], str(judul)[:50])
                skipped_items += 1
            
            # Save checkpoint every checkpoint_interval articles
            if len(processed_data) >= checkpoint_interval:
                if processed_data:
                    for item in processed_data:
                        result = output_collection.update_one(
                            {"_id": item["_id"]},
                            {"$set": {
                                "Emiten": item.get("Emiten"),
                                "Date": item.get("Date"),
                                "Title": item.get("Title") or item.get("Judul"),
                                "Link": item.get("Link"),
                                "Content": item.get("Content") or item.get("content"),
                                "Ringkasan": item["Ringkasan"],
                                "uploaded_at": item["uploaded_at"]
                            }},
                            upsert=True
                        )
                        logger.debug("Upserted document with _id=%s, matched=%d, modified=%d, upserted_id=%s",
                                    str(item["_id"]), result.matched_count, result.modified_count, str(result.upserted_id))
                    logger.info("Checkpoint: Upserted %d documents to MongoDB (Batch %d)", len(processed_data), batch_num)
                    save_checkpoint(processed_data, 1, batch_num)
                processed_data = []
                batch_num += 1
        
        # Save remaining data
        if processed_data:
            for item in processed_data:
                result = output_collection.update_one(
                    {"_id": item["_id"]},
                    {"$set": {
                        "Emiten": item.get("Emiten"),
                        "Date": item.get("Date"),
                        "Title": item.get("Title") or item.get("Judul"),
                        "Link": item.get("Link"),
                        "Content": item.get("Content") or item.get("content"),
                        "Ringkasan": item["Ringkasan"],
                        "uploaded_at": item["uploaded_at"]
                    }},
                    upsert=True
                )
                logger.debug("Upserted document with _id=%s, matched=%d, modified=%d, upserted_id=%s",
                            str(item["_id"]), result.matched_count, result.modified_count, str(result.upserted_id))
            logger.info("Final: Upserted %d documents to MongoDB (Batch %d)", len(processed_data), batch_num)
            save_checkpoint(processed_data, 1, batch_num)
        
        total_uploaded = len(news_data) - skipped_items
        logger.info("Processed %d items, upserted %d documents, skipped %d items", 
                   len(news_data), total_uploaded, skipped_items)
    
    except Exception as e:
        logger.error("Error processing news data: %s", str(e))
        raise
    finally:
        if client is not None:
            client.close()

def transform_news():
    try:
        load_dotenv()
        logger.info("Starting news transformation")
        process_news_data_from_mongo(checkpoint_interval=100)
        logger.info("News transformation completed")
    except Exception as e:
        logger.error("Error in transform_news: %s", str(e))
        raise

if __name__ == "__main__":
    transform_news()