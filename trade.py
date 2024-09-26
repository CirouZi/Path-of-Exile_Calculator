import requests
import time
import pandas as pd
import json


# 使用你取得的 Query ID 來替換 URL 中的部分
QUERY_ID = "pMLJQ3ZU0"  # 從官方網站複製的查詢 ID
API_URL = f"https://www.pathofexile.com/api/trade/search/Standard/pMLJQ3ZU0"

# 設定請求標頭
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 發送 GET 請求以獲取查詢結果
response = requests.get(API_URL, headers=HEADERS)

if response.status_code == 200:
    data = response.json()  # 將響應轉換為 JSON 格式
    print(json.dumps(data, indent=2))  # 美化輸出數據
else:
    print(f"Error fetching data, status code: {response.status_code}")