import os
import logging
import argparse
import gc
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from src.config import setup_llamaindex

# 設定日誌
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_index():
    """分批讀取 data/{dataset_name} 的檔案並建立向量庫"""
    setup_llamaindex()
    
    parser = argparse.ArgumentParser(description="建立向量索引")
    parser.add_argument("--dataset", type=str, required=True, help="要建立索引的資料集名稱")
    parser.add_argument("--batch-size", type=int, default=50, help="每批處理的文件數量 (預設 50)")
    args = parser.parse_args()
    dataset_name = args.dataset
    batch_size = args.batch_size
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', dataset_name)
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', dataset_name)

    if not os.path.exists(data_dir):
        logging.error(f"資料夾 {data_dir} 不存在。")
        return

    # 取得所有 .md 檔案列表
    all_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.md')]
    if not all_files:
        logging.error(f"資料夾 {data_dir} 內沒有 Markdown 檔案。請先執行 setup_data.py。")
        return

    logging.info(f"找到 {len(all_files)} 個檔案，將以每批 {batch_size} 個進行處理...")
    
    index = None
    
    for i in range(0, len(all_files), batch_size):
        batch_files = all_files[i : i + batch_size]
        logging.info(f"--- 正在處理批次 {i//batch_size + 1} ({len(batch_files)} 個檔案) ---")
        
        # 讀取批次資料
        reader = SimpleDirectoryReader(input_files=batch_files)
        documents = reader.load_data()
        
        # 【重要修正】顯式地進行切塊處理，並加入防禦性檢查
        from llama_index.core import Settings
        nodes = Settings.node_parser.get_nodes_from_documents(documents)
        
        # 【二次防禦】確保每個節點都沒有超過 NVIDIA 的限制，並排除 Metadata 影響
        safe_nodes = []
        for node in nodes:
            # 排除所有 Metadata 參與 Embedding 計算，避免字數溢出
            node.excluded_embed_metadata_keys = list(node.metadata.keys())
            
            # 如果發現節點文字依然過長（保守估計字元數），進行強制截斷
            # 512 token 大約等於 1500-2000 個英文字元，我們取 1200 確保安全
            if len(node.text) > 1200:
                logging.warning(f"偵測到超長節點 ({len(node.text)} chars)，進行強制截斷...")
                node.text = node.text[:1200]
            
            safe_nodes.append(node)

        logging.info(f"批次 {i//batch_size + 1}: 已將 {len(documents)} 份文件處理為 {len(safe_nodes)} 個安全節點。")

        if index is None:
            index = VectorStoreIndex(safe_nodes, show_progress=True)
        else:
            index.insert_nodes(safe_nodes)
        
        # 釋放記憶體
        del documents
        del nodes
        del safe_nodes
        gc.collect()

    if index:
        logging.info(f"全部處理完成，正在儲存至 {storage_dir} ...")
        index.storage_context.persist(persist_dir=storage_dir)
        logging.info("✅ 向量庫建立完成！隨時可以進行 RAG 查詢囉。")
    else:
        logging.warning("沒有找到可處理的內容，未建立索引。")

if __name__ == "__main__":
    build_index()
