from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    LangGraph 狀態定義
    - messages: 對話歷史紀錄，透過 add_messages 自動進行 append 操作
    - current_topic: 目前的對話主題 (Phase 3 預留)
    - is_topic_changed: 主題是否發生改變 (Phase 3 預留)
    """
    messages: Annotated[list, add_messages]
    context: str
    current_topic: str
    is_topic_changed: bool
