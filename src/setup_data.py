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

def setup_natural_questions(data_dir):
    """下載 Natural Questions 資料集"""
    zip_url = "https://github.com/google-research-datasets/natural-questions/archive/refs/heads/master.zip"
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "nq.zip")
        print(f"正在從 {zip_url} 下載 Natural Questions 資料...")
        try:
            urllib.request.urlretrieve(zip_url, zip_path)
            print("下載完成，正在解壓縮...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            src_dir = os.path.join(tmp_dir, "natural-questions-master")
            if not os.path.exists(src_dir):
                print("錯誤: 找不到 natural-questions-master 目錄。")
                return

            # 複製所有檔案
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                d = os.path.join(data_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            print(f"成功下載並解壓縮 Natural Questions 到 {data_dir}！")
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("404 錯誤，嘗試切換為 main 分支...")
                try:
                    zip_url = "https://github.com/google-research-datasets/natural-questions/archive/refs/heads/main.zip"
                    urllib.request.urlretrieve(zip_url, zip_path)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmp_dir)
                    src_dir = os.path.join(tmp_dir, "natural-questions-main")
                    if os.path.exists(src_dir):
                        for item in os.listdir(src_dir):
                            s = os.path.join(src_dir, item)
                            d = os.path.join(data_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                        print(f"成功下載並解壓縮 Natural Questions 到 {data_dir}！")
                except Exception as ex:
                    print(f"嘗試 main 分支仍下載失敗: {ex}")
            else:
                print(f"下載失敗: {e}")
        except Exception as e:
            print(f"下載失敗: {e}")

def setup_data():
    parser = argparse.ArgumentParser(description="下載測試資料集")
    parser.add_argument("--dataset", type=str, required=True, help="要建立的資料集名稱 (例如 paul_graham, natural_questions 或自訂名稱)")
    args = parser.parse_args()
    dataset_name = args.dataset
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', dataset_name)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"建立目錄: {data_dir}")

    if dataset_name == "paul_graham" or dataset_name == "dataset_a":
        setup_paul_graham(data_dir)
    elif dataset_name == "natural_questions":
        setup_natural_questions(data_dir)
    else:
        print(f"提示: 尚未內建 {dataset_name} 的自動下載邏輯。")
        print(f"請自行將 Markdown 檔案放入 {data_dir} 目錄中。")

if __name__ == "__main__":
    setup_data()
