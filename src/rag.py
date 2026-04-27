import os
import logging
from typing import Optional
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import PromptTemplate
import time
from src.config import setup_llamaindex
from src.utils.logger import log_interaction

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

def get_query_engine(dataset_name: Optional[str] = None):
    """載入 index 並回傳防護好的檢索引擎"""
    setup_llamaindex()
    
    if not dataset_name:
        dataset_name = os.getenv("DATASET_NAME", "dataset_a")
        
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', dataset_name)
    
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

def query(question: str, session_id: str = "session_default", dataset_name: Optional[str] = None) -> str:
    """執行檢索並回答使用者問題，具備嚴格例外處理與回報，並支援紀錄日誌"""
    start_time = time.time()
    
    log_data = {
        "query": question,
        "session_id": session_id,
        "endpoint_model": "unknown",
        "status": "pending"
    }

    try:
        engine = get_query_engine(dataset_name=dataset_name)
        # get_query_engine 會呼叫 setup_llamaindex，進而載入 .env
        llm_provider = os.getenv("LLM_PROVIDER", "nvidia").lower()
        if llm_provider == "vllm":
            log_data["endpoint_model"] = os.getenv("VLLM_MODEL", "gemma-4b")
        else:
            log_data["endpoint_model"] = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
        
        logger.info(f"開始搜尋問題: {question}")
        response = engine.query(question)
        
        elapsed = time.time() - start_time
        log_data["latency_seconds"] = round(elapsed, 4)
        
        # 檢查檢索結果是否為空 (LlamaIndex如果找不到任何相似節點時 source_nodes 會是空的)
        if not response.source_nodes:
            raise ValueError("Empty retrieval results")
            
        answer_str = str(response)
        log_data["answer"] = answer_str
        log_data["status"] = "success"
        
        source_contexts = []
        for node in response.source_nodes:
            source_contexts.append({
                "node_id": node.node.node_id,
                "text": node.node.get_content()[:200] + "...", 
                "score": node.score
            })
        log_data["source_contexts"] = source_contexts
        
        log_interaction(log_data)
        return answer_str
        
    except ValueError as ve:
        elapsed = time.time() - start_time
        log_data["latency_seconds"] = round(elapsed, 4)
        log_data["status"] = "error"
        log_data["error_msg"] = str(ve)
        log_data["answer"] = "I don't know based on the provided files. (系統回報：未檢索到相關內容)"
        log_interaction(log_data)
        
        logger.warning(f"檢索錯誤/無結果: {ve}")
        return log_data["answer"]
        
    except FileNotFoundError as fnfe:
        elapsed = time.time() - start_time
        log_data["latency_seconds"] = round(elapsed, 4)
        log_data["status"] = "error"
        log_data["error_msg"] = str(fnfe)
        log_data["answer"] = f"發生錯誤: {fnfe}"
        log_interaction(log_data)
        
        logger.error(f"檔案錯誤: {fnfe}")
        return log_data["answer"]
        
    except Exception as e:
        elapsed = time.time() - start_time
        log_data["latency_seconds"] = round(elapsed, 4)
        log_data["status"] = "error"
        error_msg = str(e)
        log_data["error_msg"] = error_msg
        log_data["answer"] = f"系統發生錯誤，無法處理您的請求，請稍後再試。詳細錯誤: {error_msg}"
        log_interaction(log_data)
        
        logger.error(f"遭遇不可預期的錯誤: {error_msg}")
        return log_data["answer"]
