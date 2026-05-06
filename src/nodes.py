import logging
from langchain_core.messages import SystemMessage
from src.state import AgentState
from src.rag import get_retriever, STRICT_SYSTEM_PROMPT
from src.config import get_langchain_llm

logger = logging.getLogger(__name__)

def retrieve_node(state: AgentState):
    """檢索節點：根據使用者最新的訊息檢索相關文件"""
    messages = state.get("messages", [])
    if not messages:
        return {"context": ""}
        
    last_message = messages[-1].content
    logger.info(f"Retrieve Node: 搜尋 '{last_message}'")
    
    try:
        retriever = get_retriever()
        nodes = retriever.retrieve(last_message)
        
        if not nodes:
            context = "No relevant context found."
            logger.warning("Retrieve Node: 沒有找到任何相關文件。")
        else:
            top_score = max(n.score for n in nodes if n.score is not None) if any(n.score is not None for n in nodes) else 0.0
            # 依循 Phase 1 的過濾邏輯
            if top_score > 0 and top_score < 0.65:
                 context = "Confidence too low, topic not in knowledge base."
                 logger.warning(f"Retrieve Node: 信賴度過低 (top_score={top_score:.4f} < 0.65)")
            else:
                contexts = [n.node.get_content() for n in nodes]
                context = "\n\n".join(contexts)
                logger.info(f"Retrieve Node: 成功檢索到 {len(nodes)} 筆相關文件。")
    except Exception as e:
        logger.error(f"Retrieve Node 發生錯誤: {e}")
        context = f"Error during retrieval: {e}"
        
    return {"context": context}

def generate_node(state: AgentState):
    """生成節點：結合歷史紀錄與上下文進行回答"""
    llm = get_langchain_llm()
    messages = state.get("messages", [])
    context = state.get("context", "")
    
    # 建立系統提示詞 (包含防護機制與 Context)
    system_prompt = f"{STRICT_SYSTEM_PROMPT}\n\nContext information is below.\n---------------------\n{context}\n---------------------\n"
    sys_msg = SystemMessage(content=system_prompt)
    
    # 將 SystemMessage 加在對話歷史的最前面
    full_messages = [sys_msg] + messages
    
    logger.info("Generate Node: 開始生成回答...")
    response = llm.invoke(full_messages)
    
    # 將 LLM 的回應加入到狀態的 messages 陣列中
    return {"messages": [response]}
