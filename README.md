# LGraph Agent

一個基於終端機介面 (CLI) 的 RAG (檢索增強生成) 聊天機器人，使用 LlamaIndex 進行高效的知識庫查詢。目前已整合 **NVIDIA NIM LLM** 作為主要的推理引擎，並保留 Google GenAI 作為強大的語意向量化工具。目前版本為 **第一階段 (Stateless MVP)**，專注於提供嚴格且具防幻覺機制的知識對答。

本專案預設使用 [Paul Graham 的散文集](https://github.com/ofou/graham-essays) 當作測試資料庫。

## 🎯 核心特色

* **無幻覺嚴格問答 (Strict System Prompting)**：當使用者的提問超出知識庫範圍時，機器人會強力拒絕作答，確保系統只說有依據的話。
* **LlamaIndex 本機向量庫**：利用內建的 `SimpleVectorStore` 將資料儲存於 `./storage`，不需依賴或啟動外部向量資料庫 (ChromaDB / Pinecone)。
* **Markdown 結構化切塊**：透過 `MarkdownNodeParser`，在建立 Embedding 前完整保留標題與內文的語意階層。
* **混合模型架構**：採用 NVIDIA Endpoint (`meta/llama-3.1-8b-instruct` 等) 進行快速靈活的對話推理，並搭配 Google GenAI (`models/gemini-embedding-001`) 進行精準的文件檢索。
* **QA 日誌紀錄系統**：內建日誌系統，每次查詢後自動將對話內容、耗時、參考來源與模型狀態以 JSONL 格式儲存於 `logs/qa_history.jsonl`，方便數據追蹤與效能評估。

---

## 🚀 系統需求與環境設置

### 1. 系統環境需求
* **Python 3.10+**
* 具備有效配額的 Google API Key (用於 Embedding)
* 具備有效配額的 NVIDIA API Key (用於 LLM 推理)

### 2. 安裝套件
我們建議使用虛擬環境 (Virtual Environment)，啟用後請安裝專案所需的依賴：
```bash
pip install -r requirements.txt
```

### 3. 環境變數設定
請在專案根目錄下建立一個 `.env` 檔案，並填入您的金鑰及設定：
```env
GEMINI_API_KEY="您的_GOOGLE_API_KEY"
NVIDIA_API_KEY="您的_NVIDIA_API_KEY"
NVIDIA_MODEL="meta/llama-3.1-8b-instruct"
```

### 4. 資料準備
專案中已預設提供 `data/` 目錄。若為首次使用，您會需要將所有的 Markdown `.md` 檔案放入此目錄下作為知識來源。

---

## 📖 使用指南

### 步驟一：建立本機向量索引庫
在使用機器人對話之前，需要先將 `data/` 中的 Markdown 文字檔進行切塊 (Chunking) 與向量化 (Embedding)，這段過程的產物會自動儲存到 `./storage/` 資料夾中。

在專案根目錄執行：
```bash
python -m src.ingest
```
*(注意：若資料量龐大，建立過程中可能會遇到 Gemini 基礎免費額度的 Rate Limit，請耐心等候程式執行完畢。)*

### 步驟二：啟動終端對話程式
看到 `./storage` 產生數個 JSON 檔案後，即可進入即時對答 MVP 測試階段。

```bash
python src/main.py
# 或是 python -m src.main
```

進入對話後，您可以：
1. **測試有範圍的問題**：例如：「保羅格雷厄姆認為創辦新創公司的關鍵是什麼？」
2. **測試防呆邊界**：例如：「昨晚的天氣如何？」，由於知識庫內無此資訊，系統將嚴格回應：「I don't know based on the provided files.」

要離開對話，只需輸入 `exit` 或是 `quit`。

---

## 🗺 開發藍圖 (Roadmap)
本專案的最終目標是建立一個具有持久記憶與上下文修剪能力的 Agentic 工作流，這將分為三個主要階段：

- [x] **Phase 1 (MVP)**: 基礎 Stateless RAG 應答機制與本機儲存檢索。
- [ ] **Phase 2 (Memory)**: 導入 LangGraph 的 `StateGraph` 與 Checkpointers 重建長短期記憶。
- [ ] **Phase 3 (Logic)**: 加入意圖偵測 (IntentAnalyzer) 與記憶狀態修剪機制，維持 LLM Token 使用的最佳甜蜜點。
