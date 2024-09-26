import tkinter as tk
from tkinter import ttk, messagebox
import requests

# 獲取混沌石與神聖石的即時價格
def get_currency_prices(league="Settlers"):
    url = f"https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        buy_price = None
        sell_price = None
        for currency in data['lines']:
            if currency['currencyTypeName'] == 'Divine Orb':
                buy_price = currency['chaosEquivalent']  # 買入價格
                sell_price = currency.get('receiveChaosEquivalent', buy_price)  # 賣出價格
        return buy_price, sell_price
    else:
        messagebox.showerror("錯誤", f"無法獲取即時價格: {response.status_code}")
        return None, None

# 獲取特定聖甲蟲價格
def get_scarab_prices(league="Settlers"):
    url = f"https://poe.ninja/api/data/itemoverview?league={league}&type=Scarab"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        scarab_prices = {}
        # 查找特定的聖甲蟲價格
        for scarab in data['lines']:
            if scarab['name'] in ['Ambush Scarab of Containment', 'Horned Scarab of Awakening']:
                scarab_prices[scarab['name']] = scarab['chaosValue']
        return scarab_prices
    else:
        messagebox.showerror("錯誤", f"無法獲取聖甲蟲價格: {response.status_code}")
        return None

# 更新 DC 比值
def update_dc_ratio():
    global dc_ratio
    buy_price, sell_price = get_currency_prices()
    if buy_price and sell_price:
        dc_ratio = buy_price
        messagebox.showinfo("DC 比值更新", f"目前 1 神聖石 = {dc_ratio:.2f} 混沌石")
        dc_ratio_label.config(text=f"DC 比值: {dc_ratio:.2f}")
    else:
        messagebox.showerror("錯誤", "無法獲取即時 Divine Orb 價格")

# 更新聖甲蟲價格
def update_scarab_prices():
    scarab_prices = get_scarab_prices()
    if scarab_prices:
        scarab_label.config(text=f"Ambush Scarab: {scarab_prices.get('Ambush Scarab of Containment', '未知')} 混沌石\n"
                                 f"Horned Scarab: {scarab_prices.get('Horned Scarab of Awakening', '未知')} 混沌石")

# 主 UI 設計
def setup_ui(root):
    global dc_ratio_label, scarab_label
    
    root.title("交易所計算器")

    # 主框架設置
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # DC 比值顯示與更新按鈕
    dc_ratio_label = ttk.Label(main_frame, text=f"DC 比值: {dc_ratio:.2f}")
    dc_ratio_label.grid(row=0, column=0, padx=10, pady=5)

    update_dc_button = ttk.Button(main_frame, text="更新 DC 比值", command=update_dc_ratio)
    update_dc_button.grid(row=0, column=1, padx=10, pady=5)

    # 顯示聖甲蟲價格的標籤和按鈕
    scarab_label = ttk.Label(main_frame, text="尚無聖甲蟲價格信息")
    scarab_label.grid(row=1, column=0, padx=10, pady=5)

    update_scarab_button = ttk.Button(main_frame, text="更新聖甲蟲價格", command=update_scarab_prices)
    update_scarab_button.grid(row=1, column=1, padx=10, pady=5)

# 主程序
if __name__ == "__main__":
    dc_ratio = 1.0
    root = tk.Tk()
    setup_ui(root)
    root.mainloop()
