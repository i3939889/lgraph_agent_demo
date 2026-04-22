import os
import requests
from dotenv import load_dotenv

def list_models():
    load_dotenv()
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("Error: NVIDIA_API_KEY not found in .env file.")
        return

    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"Fetching models from: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"\nTotal models found: {len(models)}")
            
            # Extract IDs
            all_ids = sorted([m.get("id", "unknown") for m in models])
            
            nvidia_models = [mid for mid in all_ids if 'nvidia' in mid.lower() or 'nemotron' in mid.lower()]
            
            print("\n=== NVIDIA / Nemotron 相關模型 ===")
            for m in nvidia_models:
                print(f" - {m}")
                
            print("\n=== 其他可用模型 (部分列出) ===")
            for m in all_ids:
                if m not in nvidia_models:
                    print(f" - {m}")
                    
        else:
            print(f"Failed. Status Code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    list_models()
