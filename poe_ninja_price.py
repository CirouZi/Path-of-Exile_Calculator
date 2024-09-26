import requests

def search_poe_trade(item_name, league="Settlers"):
    url = f"https://www.pathofexile.com/api/trade/search/{league}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    }
    
    # 查詢的物品名稱
    payload = {
        "query": {
            "status": {"option": "online"},
            "name": item_name,  # 要查詢的物品名稱
        },
        "sort": {"price": "asc"}  # 價格升序排列
    }
    
    # 發送查詢請求
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        search_result = response.json()
        return search_result['id'], search_result
    else:
        print(f"Error: {response.status_code}")
        return None, None

def fetch_poe_trade_prices(search_id, league="Settlers"):
    url = f"https://www.pathofexile.com/api/trade/fetch/{search_id}?query={search_id}&league={league}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# 測試查詢某一物品價格
search_id, search_result = search_poe_trade("Exalted Orb", league="Settlers")

if search_id:
    items_data = fetch_poe_trade_prices(search_id, league="Settlers")
    if items_data:
        for item in items_data['result']:
            price = item['listing']['price']['amount']
            currency = item['listing']['price']['currency']
            print(f"價格: {price} {currency}")
