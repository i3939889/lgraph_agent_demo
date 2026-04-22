# QA Logging 系統實作總結

我們已經成功建立並整合了對話歷史日誌 (QA Logging) 系統，為未來的效能評估與錯誤排查打下基礎。以下為本次實作的重點項目。

## 變更摘要

1. **獨立分支**：切換到了新的 Git 分支 `feature/qa-logging`。
2. **新增 Logger 模組**：
    - 新增了 `src/utils/logger.py`，專職負責將 JSON 格式的字典寫入 `.jsonl` 檔案。
    - 若 `logs/` 資料夾不存在會自動建立，並確保對話被持續追加 (append) 到 `logs/qa_history.jsonl` 中。
3. **整合至 RAG 核心 (`src/rag.py`)**：
    - 在 `query()` 函式內加入了開始與結束時間的測量，以計算實際的 **延遲時間 (Latency)**。
    - 將 `os.getenv("NVIDIA_MODEL")` 動態捕捉並記錄為 `endpoint_model`。
    - 解析 LlamaIndex 返回的 `response.source_nodes`，只擷取片段文字與分數，以減少 Log 大小但保留足夠的**參考上下文**。
    - 無論成功或遭遇例外錯誤 (Exception)，都會捕捉對應的 `status` (success/error) 寫入 Log 中。

## 驗證結果

> [!NOTE]
> 我們實際執行了一次 `query('Paul Graham')` 進行自動測試。

在 `logs/qa_history.jsonl` 中，我們成功看到了一筆完整的紀錄：
- **`latency_seconds`**: `44.6623` 秒
- **`endpoint_model`**: 捕捉了當時使用的模型
- **`source_contexts`**: 成功捕捉到了檢索的 5 個節點（Node IDs 及其文字片段與相似度分數）
- **`status`**: `success`

這證明系統可以完美地將 RAG 系統的輸入與輸出紀錄下來。

## 下一步建議

這個分支 `feature/qa-logging` 的變更目前都在您的本機儲存庫中。您可以先自行打開 `logs/qa_history.jsonl` 檢視格式是否如預期。若一切滿意，後續就可以將其 Commit 並合併回主分支。如果您想要引入其他記憶體管理 (Memory) 或進一步的代理架構功能，這個 Log 系統都能無縫銜接。
