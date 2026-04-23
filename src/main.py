import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
# 將專案根目錄加入 sys.path，這樣 python src/main.py 也能正確找到 src 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.rag import query

def main():
    # 載入 docs/.env 中的環境變數
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 未能讀取 GEMINI_API_KEY，請確認根目錄 .env 設定")
        sys.exit(1)
        
    print("Starting LGraph Agent MVP...")
    print("Type 'exit' or 'quit' to exit.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nAsk something about Paul Graham -> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("掰掰！")
                break
                
            print("Thinking...\n")
            # 呼叫 MVP 的 query 函式
            answer = query(user_input)
            print(f"Answer:\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
