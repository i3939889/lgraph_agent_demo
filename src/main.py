import os
import sys
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
        
    print("🚀 LGraph Agent MVP 測試啟動！")
    print("輸入 'exit' 或 'quit' 可以離開對話。")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n🧑‍💻 請問關於 Paul Graham 的事 👉 ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("掰掰！")
                break
                
            print("🤖 思考中...\n")
            # 呼叫 MVP 的 query 函式
            answer = query(user_input)
            print(f"✅ 回答：\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\n掰掰！")
            break
        except Exception as e:
            print(f"主迴圈發生錯誤: {e}")

if __name__ == "__main__":
    main()
