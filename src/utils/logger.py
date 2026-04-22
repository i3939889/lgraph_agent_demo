import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def log_interaction(data_dict: dict):
    """
    將 QA 互動紀錄寫入 logs/qa_history.jsonl。
    data_dict 應包含以下建議欄位 (依據實際情況填寫):
    - timestamp: ISO 8601 時間字串
    - query: 使用者的問題
    - answer: 模型的回覆
    - endpoint_model: 使用的模型或 API Endpoint
    - latency_seconds: 處理耗時
    - source_contexts: 參考的文檔段落 (list)
    - token_usage: Token 使用量 (dict)
    - session_id: 對話階段 ID
    - status: "success" 或 "error"
    - error_msg: 錯誤訊息 (如果有)
    """
    root_dir = get_project_root()
    logs_dir = os.path.join(root_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, 'qa_history.jsonl')
    
    if 'timestamp' not in data_dict:
        data_dict['timestamp'] = datetime.now().isoformat()
        
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            json_line = json.dumps(data_dict, ensure_ascii=False)
            f.write(json_line + '\n')
    except Exception as e:
        logger.error(f"寫入 QA Log 失敗: {e}")
