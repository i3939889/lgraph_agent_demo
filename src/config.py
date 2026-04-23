import os
import logging
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.nvidia import NVIDIA
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.node_parser import MarkdownNodeParser

logger = logging.getLogger(__name__)

def setup_llamaindex():
    """設定 LlamaIndex 全域使用的 Gemini 模型與切割器"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    logger.info("Loaded .env file for LLM configuration.")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("無法讀取 GEMINI_API_KEY，請確認根目錄 .env 檔案是否存在並正確設定。")

    llm_provider = os.getenv("LLM_PROVIDER", "nvidia").lower()

    if llm_provider == "vllm":
        vllm_api_base = os.getenv("VLLM_API_BASE", "http://localhost:8000/v1")
        vllm_api_key = os.getenv("VLLM_API_KEY", "empty").strip()
        vllm_model = os.getenv("VLLM_MODEL", "gemma-4b")
        # Log masked API key presence for debugging
        logger.debug(f"VLLM_API_KEY raw value (masked): {'<redacted>' if vllm_api_key else '<none>'}")
        logger.debug(f"VLLM_API_KEY length: {len(vllm_api_key) if vllm_api_key else 0}")
        if not vllm_api_key or vllm_api_key == "empty":
            logger.warning("VLLM_API_KEY not set or empty; requests to vLLM may be unauthorized.")
        else:
            logger.info("VLLM_API_KEY loaded (masked).")
        logger.debug(f"VLLM config - base: {vllm_api_base}, model: {vllm_model}")
        
        # 修正：將讀取到的 api_key 傳遞給 OpenAILike
        Settings.llm = OpenAILike(
            model=vllm_model, 
            api_base=vllm_api_base, 
            api_key=vllm_api_key if vllm_api_key != "empty" else None,
            is_chat_model=True
        )
    else:
        nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        nvidia_model = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
        if not nvidia_api_key:
            raise ValueError("無法讀取 NVIDIA_API_KEY，請確認根目錄 .env 檔案是否存在並正確設定。")
        # 設定 NVIDIA LLM
        Settings.llm = NVIDIA(model=nvidia_model, api_key=nvidia_api_key)
    # 設定 GoogleGenAI Embedding 模型
    Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=gemini_api_key)
    # 設定全局的 Node Parser 為 Markdown 解析器，以保留結構脈絡
    Settings.node_parser = MarkdownNodeParser()
