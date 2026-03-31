# 第一階段 MVP: 基礎 RAG 應答實作總結

我們已經成功將第一階段的 Stateless RAG 系統建立起來。以下是所作出的重大進展與架構重設內容：

## 1. 環境變數指引修正
原先規劃將 `.env` 放置於 `docs/` 底下，但考量到實際載入與多數工具預設邏輯，已統一修改系統讀取專案**根目錄**的 `.env`。

> [!NOTE]
> 另外已同步根據 2026 最新版的 LlamaIndex 以及 Gemini API 架構，將模型從 `gemini-1.5-flash` 升級調整為效能與支援度更好的 `gemini-2.0-flash`。Embedding 則採用對應的 `gemini-embedding-001`。

## 2. `.gitignore` 設定
如您所要求，除了排除一般的 Python 暫存檔、虛擬環境 (Virtual Environment) 之外，已經將 `data/` 與 `./storage/` 加入了 `.gitignore`，確保您未來的版本控制中不會混入這些大體積、會反覆重建的本地資料。

## 3. 核心模組實作完成
1. **`src/config.py`**: 中央控管 LlamaIndex 所需要存取 Gemini 模型的介面。另外也將 `MarkdownNodeParser` 註冊進去，這使得我們放入的 Paul Graham 文章在切分 Chunk 時，能完美保留標題（Headers）上的語義，強化後續檢索準確度。
2. **`src/ingest.py`**: 利用設計好的 Config，掃描 `data/` 下面的 `.md` 檔案，全自動轉成向量，並將資料落地化儲存於 `./storage/` 資料夾，免去日後反覆重新計算的龐大開銷。
3. **`src/rag.py`**: 將 `./storage/` 的向量還原成 Query Engine 檢索引擎。包含了強制必須僅根據知識庫回答的 System Prompt 防護機制。並且依照您的要求，實作了防禦性的 `try-except` 邏輯，當這套 RAG 引擎遇到空的結果、Rate Limits 或尚未建立資料夾的例外時，都會回傳安全的防禦性文字回覆給使用者。
4. **`src/main.py`**: 原有的進入點改為一個無限問答的終端機即時互動迴圈。

## 4. 當前與後續測試步驟

> [!WARNING]
> 目前系統背景正在為您默默執行 `python -m src.ingest` 指令！由於共有高達 231 篇散文需要進行切塊與 API 向量化 (Embedding)，通常受限於 API Rate Limit，這可能需要幾分鐘的時間跑完。您隨時可以自己透過 `ls storage` 或觀察根目錄來發現是否產生了向量存檔。

一旦產生 `./storage/` 資料夾後，您只需開啟 Terminal 並輸入指令：

```bash
python -m src.main
```

機器人就會上線，您可以嘗試用中英文與他討教 Paul Graham 的所有經典文章，並測試它是否會在超出範圍的情境下乖乖回答「I don't know based on the provided files.」！
