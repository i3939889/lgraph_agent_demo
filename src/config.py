import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.llms.nvidia import NVIDIA
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.node_parser import MarkdownNodeParser

def setup_llamaindex():
    """設定 LlamaIndex 全域使用的 Gemini 模型與切割器"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("無法讀取 GEMINI_API_KEY，請確認根目錄 .env 檔案是否存在並正確設定。")

    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    nvidia_model = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
    if not nvidia_api_key:
        raise ValueError("無法讀取 NVIDIA_API_KEY，請確認根目錄 .env 檔案是否存在並正確設定。")

    # 設定 NVIDIA LLM
    Settings.llm = NVIDIA(model=nvidia_model, api_key=nvidia_api_key)
    # 設定 Gemini Embedding 模型
    Settings.embed_model = GeminiEmbedding(model_name="models/gemini-embedding-001", api_key=gemini_api_key)
    # 設定全局的 Node Parser 為 Markdown 解析器，以保留結構脈絡
    Settings.node_parser = MarkdownNodeParser()
