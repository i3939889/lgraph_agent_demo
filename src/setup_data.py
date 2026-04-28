import os
import urllib.request
import zipfile
import shutil
import tempfile

import argparse

def setup_paul_graham(data_dir):
    """下載 Paul Graham 散文集"""
    zip_url = "https://github.com/lmmsoft/paul_graham_essays/archive/refs/heads/main.zip"
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "essays.zip")
        print(f"正在從 {zip_url} 下載 Paul Graham 資料...")
        try:
            urllib.request.urlretrieve(zip_url, zip_path)
            print("下載完成，正在解壓縮...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            src_essays_dir = os.path.join(tmp_dir, "paul_graham_essays-main", "pg_essays")
            if not os.path.exists(src_essays_dir):
                print("錯誤: 找不到 pg_essays 目錄。")
                return

            md_files = [f for f in os.listdir(src_essays_dir) if f.endswith('.md')]
            print(f"找到 {len(md_files)} 個散文檔案，正在搬移至 {data_dir}...")
            count = 0
            for f in md_files:
                src_path = os.path.join(src_essays_dir, f)
                dest_path = os.path.join(data_dir, f)
                shutil.copy2(src_path, dest_path)
                count += 1
            print(f"成功下載並解壓縮 {count} 篇散文到 {data_dir}！")
        except Exception as e:
            print(f"下載失敗: {e}")

def setup_natural_questions(data_dir, limit=20):
    """下載 Natural Questions 資料集並轉換為 Markdown"""
    print(f"正在透過 Hugging Face Datasets 獲取 Natural Questions 數據 (限制 {limit} 筆)...")
    try:
        from datasets import load_dataset
    except ImportError:
        print("錯誤: 找不到 datasets 套件。請先執行 `pip install datasets`。")
        return

    try:
        # 下載小部分的驗證集作為測試
        dataset = load_dataset('natural_questions', split=f'train[:{limit}]', trust_remote_code=True)
        
        count = 0
        for i, item in enumerate(dataset):
            question = item.get('question', {}).get('text', 'Unknown Question')
            
            # 取得文件內容 (從 HTML tokens 中提取文字)
            document_tokens = item.get('document', {}).get('tokens', [])
            is_html = item.get('document', {}).get('is_html', [])
            
            # 過濾掉 HTML 標籤，只保留文字內容
            text_parts = []
            for token, html_flag in zip(document_tokens, is_html):
                if not html_flag:
                    text_parts.append(token)
            
            context_text = " ".join(text_parts[:2000]) # 限制長度避免單一檔案過大
            
            # 取得答案 (如果有的話)
            annotations = item.get('annotations', {})
            short_answers = annotations.get('short_answers', [])
            ans_str = "N/A"
            if short_answers and len(short_answers) > 0:
                # 這裡簡單取第一個短答案的 token 範圍 (簡化邏輯)
                ans_str = "See context for details"

            md_content = f"# Question: {question}\n\n**Potential Answer:** {ans_str}\n\n## Source Document Context\n\n{context_text}\n"
            
            file_path = os.path.join(data_dir, f"nq_sample_{i}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            count += 1

        print(f"成功下載並轉換 {count} 筆 Natural Questions 資料到 {data_dir}！")
            
    except Exception as e:
        print(f"處理 Natural Questions 時發生錯誤: {e}")

def setup_trivia_qa(data_dir, limit):
    """下載並轉換 TriviaQA RC 資料集為 Markdown 格式"""
    print(f"正在透過 Hugging Face Datasets 獲取 TriviaQA (RC) 資料集，預計取得 {limit} 筆資料...")
    try:
        from datasets import load_dataset
    except ImportError:
        print("錯誤: 找不到 datasets 套件。請先執行 `pip install datasets`。")
        return

    try:
        # 使用 split 參數來限制下載與處理的數量，避免記憶體或下載時間過長
        dataset = load_dataset('trivia_qa', 'rc', split=f'train[:{limit}]')
        
        count = 0
        for i, item in enumerate(dataset):
            question = item.get('question', 'Unknown Question')
            question_id = item.get('question_id', f'q_{i}')
            answer_val = item.get('answer', {}).get('value', 'Unknown Answer')
            
            # 收集 Context (從 Wikipedia entity pages 或 search results)
            contexts = []
            if 'entity_pages' in item and item['entity_pages']:
                for page in item['entity_pages'].get('wiki_context', []):
                    if page:
                        contexts.append(page)
            if 'search_results' in item and item['search_results']:
                for res in item['search_results'].get('search_context', []):
                    if res:
                        contexts.append(res)
            
            context_text = "\n\n".join(contexts) if contexts else "No context available."
            
            md_content = f"# Question: {question}\n\n**Answer:** {answer_val}\n\n## Context\n\n{context_text}\n"
            
            # 寫入 Markdown 檔案
            file_path = os.path.join(data_dir, f"trivia_qa_{question_id}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            count += 1

        print(f"成功下載並轉換 {count} 筆 TriviaQA 資料到 {data_dir}！")
    except Exception as e:
        print(f"處理 TriviaQA 時發生錯誤: {e}")


def setup_data():
    parser = argparse.ArgumentParser(description="下載測試資料集")
    parser.add_argument("--dataset", type=str, required=True, help="要建立的資料集名稱 (例如 paul_graham, natural_questions, trivia_qa 或自訂名稱)")
    parser.add_argument("--limit", type=int, default=100, help="限制處理的資料筆數 (預設 100 筆，僅支援部分資料集如 trivia_qa)")
    args = parser.parse_args()
    dataset_name = args.dataset
    limit = args.limit
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', dataset_name)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"建立目錄: {data_dir}")

    if dataset_name == "paul_graham" or dataset_name == "dataset_a":
        setup_paul_graham(data_dir)
    elif dataset_name == "natural_questions":
        setup_natural_questions(data_dir)
    elif dataset_name == "trivia_qa":
        setup_trivia_qa(data_dir, limit)
    else:
        print(f"提示: 尚未內建 {dataset_name} 的自動下載邏輯。")
        print(f"請自行將 Markdown 檔案放入 {data_dir} 目錄中。")

if __name__ == "__main__":
    setup_data()
