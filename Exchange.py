import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

class ExchangeRateApp:
    NINJA_CURRENCY_API_URL = "https://poe.ninja/api/data/currencyoverview?league=Settlers&type=Currency"
    NINJA_FRAGMENT_API_URL = "https://poe.ninja/api/data/itemoverview?league=Settlers&type=Fragment"
    NINJA_SCARAB_API_URL = "https://poe.ninja/api/data/itemoverview?league=Settlers&type=Scarab"

    def __init__(self, root):
        self.root = root
        self.root.title("交易所比值計算器")

        # 初始化變數
        self.currency_items = {}  # 通貨類（如 Divine Orb 和 Chaos Orb）
        self.fragment_items = {}  # 碎片類
        self.scarab_items = {}    # 聖甲蟲類
        self.selected_want_item = tk.StringVar(value="選擇物品")
        self.selected_have_item = tk.StringVar(value="選擇通貨")
        self.exchange_rate = tk.StringVar(value="1:0.00")

        # 設置 UI
        self.setup_ui()

        # 加載物品價格數據 (在新線程中運行)
        threading.Thread(target=self.load_items_from_api).start()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # I Want 下拉選單
        ttk.Label(main_frame, text="I Want").grid(row=0, column=0, sticky=tk.W)
        self.want_menu = ttk.OptionMenu(main_frame, self.selected_want_item, "Loading...")  # 初始化時顯示"Loading..."
        self.want_menu.grid(row=0, column=1, padx=5, pady=5)

        # I Have 下拉選單
        ttk.Label(main_frame, text="I Have").grid(row=1, column=0, sticky=tk.W)
        self.have_menu = ttk.OptionMenu(main_frame, self.selected_have_item, "Loading...")  # 初始化時顯示"Loading..."
        self.have_menu.grid(row=1, column=1, padx=5, pady=5)

        # 顯示比率
        ttk.Label(main_frame, text="交換比率").grid(row=2, column=0, sticky=tk.W)
        self.rate_label = ttk.Label(main_frame, textvariable=self.exchange_rate)
        self.rate_label.grid(row=2, column=1, padx=5, pady=5)

        # 計算按鈕
        calculate_button = ttk.Button(main_frame, text="計算", command=self.calculate_exchange_rate)
        calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

    def load_items_from_api(self):
        """從 API 獲取最新的物品和通貨數據"""
        try:
            # 加載數據，聯盟名稱為大寫 Settlers
            currency_data = self.fetch_data(self.NINJA_CURRENCY_API_URL)
            fragment_data = self.fetch_data(self.NINJA_FRAGMENT_API_URL)
            scarab_data = self.fetch_data(self.NINJA_SCARAB_API_URL)

            # 提取數據並分類
            self.extract_currency_items(currency_data)   # 提取通貨類數據
            self.extract_items(fragment_data, self.fragment_items, 'name', 'chaosValue')   # 提取碎片類數據
            self.extract_items(scarab_data, self.scarab_items, 'name', 'chaosValue')   # 提取聖甲蟲類數據

            # 更新選單
            self.update_menus()

        except Exception as e:
            messagebox.showerror("錯誤", f"無法加載數據: {e}")

    def fetch_data(self, url):
        """從指定的 URL 加載數據"""
        try:
            response = requests.get(url)
            response.raise_for_status()  # 檢查請求是否成功
            return response.json()
        except requests.RequestException as e:
            print(f"API 請求失敗: {e}")
            raise

    def extract_currency_items(self, data):
        """提取通貨類中的 Divine Orb 和 Chaos Orb"""
        for currency in data["lines"]:
            if currency["currencyTypeName"] in ["Divine Orb", "Chaos Orb"]:
                self.currency_items[currency["currencyTypeName"]] = currency["chaosEquivalent"]

    def extract_items(self, data, target_dict, name_key, value_key):
        """從數據中提取物品名稱和價格，分類到目標字典"""
        for item in data["lines"]:
            target_dict[item[name_key]] = item[value_key]

    def update_menus(self):
        """更新 I Want 和 I Have 的下拉選單"""
        if not self.currency_items and not self.fragment_items and not self.scarab_items:
            print("No items to display in the menus.")
            return

        # 將不同類別的物品進行分類並顯示
        menu_items = list(self.currency_items.keys()) + list(self.fragment_items.keys()) + list(self.scarab_items.keys())

        # 更新 I Want 選單，包括通貨、碎片和聖甲蟲
        self.want_menu["menu"].delete(0, "end")  # 清空當前選項
        for item in menu_items:
            self.want_menu["menu"].add_command(label=item, command=tk._setit(self.selected_want_item, item))

        # 更新 I Have 選單，包括通貨 Divine Orb 和 Chaos Orb
        self.have_menu["menu"].delete(0, "end")  # 清空當前選項
        for item in self.currency_items.keys():
            self.have_menu["menu"].add_command(label=item, command=tk._setit(self.selected_have_item, item))

        # 設置初始值
        if menu_items:
            self.selected_want_item.set(menu_items[0])
            self.selected_have_item.set(list(self.currency_items.keys())[0])

    def calculate_exchange_rate(self):
        """計算 I Want 和 I Have 之間的交換比率"""
        want_item = self.selected_want_item.get()
        have_item = self.selected_have_item.get()

        # 判斷 I Want 和 I Have 是否有效
        if want_item in self.currency_items:
            want_price = self.currency_items[want_item]
        elif want_item in self.fragment_items:
            want_price = self.fragment_items[want_item]
        elif want_item in self.scarab_items:
            want_price = self.scarab_items[want_item]
        else:
            messagebox.showerror("錯誤", "請選擇有效的物品")
            return

        if have_item in self.currency_items:
            have_price = self.currency_items[have_item]
        else:
            messagebox.showerror("錯誤", "請選擇有效的通貨")
            return

        # 計算交換比率
        rate = want_price / have_price
        self.exchange_rate.set(f"1:{rate:.2f}")

# 主程序運行
if __name__ == "__main__":
    root = tk.Tk()
    app = ExchangeRateApp(root)
    root.mainloop()
