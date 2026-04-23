import os
import urllib.request
import zipfile
import shutil
import tempfile

def setup_data():
    """下載 Paul Graham 的散文集作為測試資料"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    zip_url = "https://github.com/lmmsoft/paul_graham_essays/archive/refs/heads/main.zip"
    
    # 確保 data 目錄存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"建立目錄: {data_dir}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "essays.zip")
        print(f"正在從 {zip_url} 下載資料...")
        
        try:
            # 下載 zip 檔案
            urllib.request.urlretrieve(zip_url, zip_path)
            
            # 解壓縮
            print("下載完成，正在解壓縮...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            # 來源目錄 (GitHub 下載下來的 zip 會有一層 repository-branch 的資料夾)
            src_essays_dir = os.path.join(tmp_dir, "paul_graham_essays-main", "pg_essays")
            
            if not os.path.exists(src_essays_dir):
                print("錯誤: 在下載的檔案中找不到 pg_essays 目錄。")
                return

            md_files = [f for f in os.listdir(src_essays_dir) if f.endswith('.md')]
            print(f"找到 {len(md_files)} 個散文檔案，正在搬移至 {data_dir}...")
            
            # 搬移檔案
            count = 0
            for f in md_files:
                src_path = os.path.join(src_essays_dir, f)
                dest_path = os.path.join(data_dir, f)
                # 只有當檔案不存在，或是需要覆蓋時才複製
                shutil.copy2(src_path, dest_path)
                count += 1
                
            print(f"成功下載並解壓縮 {count} 篇散文到 data/ 目錄！")
            
        except urllib.error.URLError as e:
            print(f"下載失敗: {e}")
        except zipfile.BadZipFile:
            print("下載的檔案不是有效的 ZIP 壓縮檔。")
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")

if __name__ == "__main__":
    setup_data()
