import os
import sys
import logging
import argparse

logging.basicConfig(level=logging.INFO)
# 將專案根目錄加入 sys.path，這樣 python src/main.py 也能正確找到 src 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.graph import build_graph

def main():
    parser = argparse.ArgumentParser(description="LGraph Agent Phase 2")
    parser.add_argument("--dataset", type=str, default=None, help="指定資料集名稱 (覆蓋 .env 中的 DATASET_NAME)")
    args = parser.parse_args()
    
    # 載入 docs/.env 中的環境變數
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    
    # 設定 dataset (讓 retriever 能抓取)
    active_dataset = args.dataset if args.dataset else os.getenv("DATASET_NAME", "default_dataset")
    os.environ["DATASET_NAME"] = active_dataset
        
    print("Starting LGraph Agent Phase 2 (Memory)...")
    print("Type 'exit' or 'quit' to exit.")
    print("-" * 50)
    
    # 建立 LangGraph
    app = build_graph()
    
    # 固定 thread_id 達成單一 Session 記憶
    config = {"configurable": {"thread_id": "session_default"}}
    
    while True:
        try:
            user_input = input(f"\nAsk something about {active_dataset} -> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("掰掰！")
                break
                
            print("Thinking...\n")
            
            # 使用 Graph 進行對話推論
            initial_state = {"messages": [HumanMessage(content=user_input)]}
            
            for event in app.stream(initial_state, config):
                for node_name, node_state in event.items():
                    if node_name == "generate":
                        answer = node_state["messages"][-1].content
                        print(f"Answer:\n{answer}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
