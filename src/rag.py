import os
import logging
from typing import Optional
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import PromptTemplate
from src.config import setup_llamaindex

logger = logging.getLogger(__name__)

# 防護系統提示詞
STRICT_SYSTEM_PROMPT = """
You are an AI assistant designed to answer questions strictly based on the provided context.
If you don't know the answer or if the provided context does not contain enough information to answer the question, you must say "I don't know based on the provided files."
Do not attempt to guess or provide information from outside the context.
"""

QA_PROMPT_TMPL = (
    STRICT_SYSTEM_PROMPT + "\n"
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer: "
)

def get_query_engine():
    """載入 index 並回傳防護好的檢索引擎"""
    setup_llamaindex()
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
    
    if not os.path.exists(storage_dir):
        raise FileNotFoundError(f"找不到向量庫 {storage_dir}，請先執行 src/ingest.py 建立。")
        
    logger.info("正在讀取本機向量庫...")
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context)
    
    # 建立 query_engine
    query_engine = index.as_query_engine(similarity_top_k=5)
    
    # 設定防幻覺 Prompt
    qa_prompt = PromptTemplate(QA_PROMPT_TMPL)
    query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt})
    
    return query_engine

def query(question: str) -> str:
    """執行檢索並回答使用者問題，具備嚴格例外處理與回報"""
    try:
        engine = get_query_engine()
        logger.info(f"開始搜尋問題: {question}")
        response = engine.query(question)
        
        # 檢查檢索結果是否為空 (LlamaIndex如果找不到任何相似節點時 source_nodes 會是空的)
        if not response.source_nodes:
            raise ValueError("Empty retrieval results")
            
        return str(response)
        
    except ValueError as ve:
        # 攔截自定的 ValueError 如空檢索
        logger.warning(f"檢索錯誤/無結果: {ve}")
        return "I don't know based on the provided files. (系統回報：未檢索到相關內容)"
        
    except FileNotFoundError as fnfe:
        # 未建立向量庫的例外
        logger.error(f"檔案錯誤: {fnfe}")
        return f"發生錯誤: {fnfe}"
        
    except Exception as e:
        # 其他 API 等級例外攔截 (如 Rate Limit, Network Error 等)
        error_msg = str(e)
        logger.error(f"遭遇不可預期的錯誤: {error_msg}")
        return f"系統發生錯誤，無法處理您的請求，請稍後再試。詳細錯誤: {error_msg}"
