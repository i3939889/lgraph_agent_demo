import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from src.config import setup_llamaindex

# 設定日誌
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_index():
    """讀取 data/ 的 Markdown 檔案，以 Gemini embedding 建立向量庫並儲存至 storage/"""
    setup_llamaindex()
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')

    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        logging.error(f"資料夾 {data_dir} 不存在或為空。請先準備好 Markdown 檔案。")
        return

    logging.info(f"開始載入 {data_dir} 內的檔案...")
    # 讀取資料
    reader = SimpleDirectoryReader(input_dir=data_dir, required_exts=[".md"])
    documents = reader.load_data()
    logging.info(f"成功載入 {len(documents)} 份獨立文件片段。")

    logging.info("開始進行向量化並建立本機索引庫 (VectorStoreIndex)...")
    index = VectorStoreIndex.from_documents(documents)

    logging.info(f"建立完成，正在發佈並儲存至 {storage_dir} ...")
    index.storage_context.persist(persist_dir=storage_dir)
    logging.info("✅ 向量庫建立完成！隨時可以進行 RAG 查詢囉。")

if __name__ == "__main__":
    build_index()
