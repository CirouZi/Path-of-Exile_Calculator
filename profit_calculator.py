import json
import os

# 建立一個列表來存儲所有品項的數據
items = []

# 文件名常量
DATA_FILE = "items_data.json"

def load_items_from_file():
    # 從文件中加載已保存的數據
    global items
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
        print(f"已加載 {len(items)} 個已保存的物品數據。")
    else:
        print("沒有找到數據文件，將從空數據開始。")

def save_items_to_file():
    # 將數據保存到文件中
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    print("物品數據已保存到文件。")

def input_item_data():
    # 輸入物品名稱和價格信息
    item_name = input("請輸入物品名稱: ")

    try:
        # 輸入 {item_name} 在 I Have、C 在 I Want 的價格與庫存量
        chaos_buy = float(input(f"請輸入 {item_name} 在 I Have、混沌石 (C) 在 I Want 的比值: "))
        chaos_buy_stock = int(input(f"請輸入 {item_name} 在 I Have、混沌石 (C) 在 I Want 的庫存量: "))
        
        # 輸入 {item_name} 在 I Want、C 在 I Have 的價格與庫存量
        chaos_sell = float(input(f"請輸入 {item_name} 在 I Want、混沌石 (C) 在 I Have 的比值: "))
        chaos_sell_stock = int(input(f"請輸入 {item_name} 在 I Want、混沌石 (C) 在 I Have 的庫存量: "))
        
        # 輸入 {item_name} 在 I Want、D 在 I Want 的價格與庫存量
        divine_sell = float(input(f"請輸入 {item_name} 在 I Want、神聖石 (D) 在 I Want 的比值: "))
        divine_sell_stock = int(input(f"請輸入 {item_name} 在 I Want、神聖石 (D) 在 I Want 的庫存量: "))
        
        # 輸入該物品的金幣成本
        item_coin_value = float(input(f"請輸入 {item_name} 的金幣成本: "))
    except ValueError:
        print("請輸入正確的數字格式")
        return None

    return {
        "name": item_name,
        "chaos_buy": chaos_buy,
        "chaos_buy_stock": chaos_buy_stock,
        "chaos_sell": chaos_sell,
        "chaos_sell_stock": chaos_sell_stock,
        "divine_sell": divine_sell,
        "divine_sell_stock": divine_sell_stock,
        "coin_value": item_coin_value
    }

def calculate_profit(item, chaos_to_divine_ratio, chaos_to_coin_ratio):
    # 計算C賣出的利潤
    chaos_profit = item["chaos_sell"] - item["chaos_buy"]
    
    # 將D賣出的價格轉換為C，並計算利潤
    divine_sell_in_chaos = item["divine_sell"] * chaos_to_divine_ratio
    divine_profit = divine_sell_in_chaos - item["chaos_buy"]
    
    # 顯示利潤分析
    print(f"\n{item['name']} 的利潤分析:")
    print(f" - C賣出利潤: {chaos_profit:.2f}C")
    print(f" - D賣出利潤折合C: {divine_profit:.2f}C")
    
    # 計算物品的金幣成本並將其轉換為C成本
    item_cost_in_chaos = item["coin_value"] / chaos_to_coin_ratio
    print(f" - {item['name']} 的金幣成本折合C: {item_cost_in_chaos:.2f}C")

    # 計算扣除金幣成本後的最終利潤
    final_chaos_profit = chaos_profit - item_cost_in_chaos
    final_divine_profit = divine_profit - item_cost_in_chaos

    print(f" - 扣除金幣成本後的C賣出最終利潤: {final_chaos_profit:.2f}C")
    print(f" - 扣除金幣成本後的D賣出最終利潤（折合C）: {final_divine_profit:.2f}C")

    # 根據庫存推薦最快賣出的方式
    print(f"\n{item['name']} 的庫存分析:")
    print(f" - C購買庫存量: {item['chaos_buy_stock']}")
    print(f" - C販賣庫存量: {item['chaos_sell_stock']}")
    print(f" - D販賣庫存量: {item['divine_sell_stock']}")

    if item["divine_sell_stock"] > item["chaos_sell_stock"]:
        print(f"推薦使用D進行交易，因為庫存量較多，賣出會更快。")
    else:
        print(f"推薦使用C進行交易，因為庫存量較多，賣出會更快。")

def query_items(keyword, chaos_to_divine_ratio, chaos_to_coin_ratio):
    # 根據關鍵字查詢已存儲的品項
    print(f"\n關鍵字 '{keyword}' 的查詢結果:")
    found_items = [item for item in items if keyword.lower() in item["name"].lower()]
    
    if found_items:
        for item in found_items:
            print(f"物品名稱: {item['name']}")
            print(f"  - C購買價格: {item['chaos_buy']}C, 庫存: {item['chaos_buy_stock']}")
            print(f"  - C販賣價格: {item['chaos_sell']}C, 庫存: {item['chaos_sell_stock']}")
            print(f"  - D販賣價格: {item['divine_sell']}D, 庫存: {item['divine_sell_stock']}")
            print(f"  - 金幣成本: {item['coin_value']}")
            print("-------------------------------------------------------")
            
            # 詢問是否要修改比值或庫存
            modify = input(f"是否要修改 {item['name']} 的數據？(y/n): ").lower()
            if modify == 'y':
                try:
                    item['chaos_buy'] = float(input(f"請輸入 {item['name']} 新的C購買價格: "))
                    item['chaos_buy_stock'] = int(input(f"請輸入 {item['name']} 新的C購買庫存量: "))
                    item['chaos_sell'] = float(input(f"請輸入 {item['name']} 新的C販賣價格: "))
                    item['chaos_sell_stock'] = int(input(f"請輸入 {item['name']} 新的C販賣庫存量: "))
                    item['divine_sell'] = float(input(f"請輸入 {item['name']} 新的D販賣價格: "))
                    item['divine_sell_stock'] = int(input(f"請輸入 {item['name']} 新的D販賣庫存量: "))
                    
                    # 再次進行利潤計算
                    calculate_profit(item, chaos_to_divine_ratio, chaos_to_coin_ratio)
                    
                    # 保存修改後的數據
                    save_items_to_file()
                except ValueError:
                    print("請輸入正確的數字格式。")
    else:
        print("沒有找到匹配的品項。")

def main():
    # 每次運行程式時從文件加載數據
    load_items_from_file()

    # 固定的C對D比值
    chaos_to_divine_ratio = float(input("請輸入D與C的比值: "))
    chaos_to_coin_ratio = 25

    while True:
        action = input("請選擇操作: (1) 輸入新物品 (2) 查詢物品 (3) 結束: ")

        if action == '1':
            # 輸入並計算新的物品
            item_data = input_item_data()
            if item_data is not None:
                items.append(item_data)  # 保存物品數據
                calculate_profit(item_data, chaos_to_divine_ratio, chaos_to_coin_ratio)
                save_items_to_file()  # 保存數據到文件
        
        elif action == '2':
            # 查詢物品
            keyword = input("請輸入查詢關鍵字: ")
            query_items(keyword, chaos_to_divine_ratio, chaos_to_coin_ratio)

        elif action == '3':
            save_items_to_file()  # 程式結束前保存數據
            break

        else:
            print("無效操作，請重新選擇。")

if __name__ == "__main__":
    main()
