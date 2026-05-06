from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.nodes import retrieve_node, generate_node

def build_graph():
    """建立並編譯具有記憶體的 LangGraph Workflow"""
    workflow = StateGraph(AgentState)
    
    # 註冊節點
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    # 建立連接
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # 設定 Checkpointer (單一 session 記憶體)
    memory = MemorySaver()
    
    # 編譯圖
    app = workflow.compile(checkpointer=memory)
    return app
