import sys
import os

sys.path.append(os.path.dirname(__file__))

from src.config import setup_llamaindex
from llama_index.core import Settings

if __name__ == "__main__":
    print("Setting up llamaindex with vllm...")
    setup_llamaindex()
    print("Testing vLLM connection by generating completion...")
    try:
        response = Settings.llm.complete("Hello, how are you?")
        print("Response from vLLM:", response)
    except Exception as e:
        print("Error connecting to vLLM:", e)
