import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import json
import os
import csv
import re  # 引入正則表達式模組
from typing import List, Dict
from fractions import Fraction  # 引入 fractions 模組以處理分數


# 將物品的計算邏輯抽離到獨立的類
class ItemCalculator:
    @staticmethod
    def calculate_profit(item: Dict, current_chaos: float, dc_ratio: float, item_coin_value: float):
        # 初始化缺失的鍵
        item.setdefault('extra_coin', 0.0)
        item.setdefault('profit_c_to_c', 0.0)
        item.setdefault('profit_c_to_d', 0.0)
        item.setdefault('purchasable_with_chaos', 0)
        item.setdefault('receive_coin', 0.0)
        item.setdefault('sell_coin', 0.0)
        item.setdefault('avg_coin_c', 0.0)
        item.setdefault('sell_div_coin', 0.0)
        item.setdefault('avg_coin_d', 0.0)
        item.setdefault('avg_coin_d_extra', 0.0)
        item.setdefault('total_profit_c_to_c', 0.0)
        item.setdefault('total_profit_c_to_d', 0.0)
        item.setdefault('required_chaos', 0.0)  # 新增的鍵

        # 加上這段初始化可購買數量的邏輯
        if 'purchasable_with_chaos' not in item or item['purchasable_with_chaos'] == 0:
            item['purchasable_with_chaos'] = int(current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0

        receive_price = item['receive_price']  # 購買價格 (混沌石)
        sell_price = item['sell_price']  # 出售價格 (混沌石)
        divine_sell_price = item['divine_sell_price']  # 神聖石價格 (神聖石)

        # C收C賣利潤計算
        item['profit_c_to_c'] = round(sell_price - receive_price, 2)

        # C買D賣利潤計算
        sell_div_num_chaos = round(divine_sell_price * dc_ratio, 2)  # 神聖石販賣價格轉混沌石價值
        item['profit_c_to_d'] = round(sell_div_num_chaos - receive_price, 2)

        # 可購買數量
        # item['purchasable_with_chaos'] = int(current_chaos // receive_price) if receive_price > 0 else 0

        # 計算所需C
        item['required_chaos'] = item['purchasable_with_chaos'] * receive_price  # 所需C = 購買數量 * 購買價格

        # C收C賣總利潤計算
        item['total_profit_c_to_c'] = round(item['profit_c_to_c'] * item['purchasable_with_chaos'], 2)

        # C買D賣總利潤計算
        item['total_profit_c_to_d'] = round(item['profit_c_to_d'] * item['purchasable_with_chaos'], 2)

        # C收C賣金幣計算
        item['receive_coin'] = round(item_coin_value * item['purchasable_with_chaos'], 2)  # 購買物品的金幣消耗
        item['sell_coin'] = round(item['purchasable_with_chaos'] * sell_price, 2)  # 出售物品的金幣收益
        all_coin_c = round(item['receive_coin'], 2)  # C收C賣的總金幣消耗（注意：不包括賣出的金幣收益）
        avg_coin_c = round(all_coin_c / item['total_profit_c_to_c'], 2) if item['total_profit_c_to_c'] > 0 else 0
        item['avg_coin_c'] = avg_coin_c

        # C買D賣金幣計算
        item['sell_div_coin'] = round(item['purchasable_with_chaos'] * sell_div_num_chaos, 2)  # C買D賣的金幣收益
        all_coin_d = round(item['receive_coin'] + item['sell_div_coin'], 2)  # C買D賣的總金幣消耗
        avg_coin_d = round(all_coin_d / item['profit_c_to_d'], 2) if item['profit_c_to_d'] > 0 else "無法計算（虧損）"
        item['avg_coin_d'] = avg_coin_d

        # 使用新邏輯來計算 avg_coin_d 和 avg_coin_d_extra
        if item['total_profit_c_to_d'] <= 0:
            # 當交易利潤為負數或等於 0
            item['avg_coin_d'] = "無法計算（虧損）"
            item['avg_coin_d_extra'] = "無法計算（虧損）"
        else:
            # 正常情況下計算
            item['avg_coin_d'] = round(all_coin_d / item['total_profit_c_to_d'], 2)
            item['avg_coin_d_extra'] = round((all_coin_d + item['extra_coin']) / item['total_profit_c_to_d'], 2)

        # 額外金幣成本計算 (D換C)
        extra_coin = round(item['purchasable_with_chaos'] * 25, 2)  # D換C 額外支付的金幣
        item['extra_coin'] = extra_coin
        avg_coin_d_extra = round((all_coin_d + extra_coin) / item['profit_c_to_d'], 2) if item['profit_c_to_d'] > 0 else "無法計算（虧損）"
        item['avg_coin_d_extra'] = avg_coin_d_extra

        # Debug prints for verification
        # print(f"購買價格: {receive_price} chaos")
        # print(f"販賣價格: {sell_price} chaos")
        # print(f"神聖石販賣價格: {divine_sell_price} divine")
        # print(f"當前DC比率: {dc_ratio}")
        # print(f"單位物品價值: {item_coin_value} 金幣")
        # print(f"--------------------------------")
        # print(f"C收C賣，利潤是: {item['profit_c_to_c']} C")
        # print(f"C收C賣，總利潤是: {item['total_profit_c_to_c']} C")
        # print(f"C收C賣，消耗金幣是: {all_coin_c}")
        # print(f"C收C賣，平均賺1C需要的金幣是: {item['avg_coin_c']}")
        # print(f"--------------------------------")
        # print(f"C買D賣的利潤是: {item['profit_c_to_d']} C")
        # print(f"C買D賣，總利潤是: {item['total_profit_c_to_d']} C")
        # print(f"C買D賣消耗的金幣是: {all_coin_d}")
        # print(f"C買D賣，平均賺1C需要的金幣是: {item['avg_coin_d']}")
        # print(f"從Faustus換C需要額外支付{extra_coin}金幣，因此平均賺1C需要的金幣是: {item['avg_coin_d_extra']}")
        # print(f"--------------------------------")


# UI 和主要邏輯類
class ItemManagerApp:
    DATA_FILE = "items_data_v2.json"

    def __init__(self, root):
        self.root = root
        self.root.title("交易計算器")

        # 初始化變數
        self.items: List[Dict] = []
        self.current_chaos = 0.0
        self.dc_ratio = 1.0  # 神聖石匯率初始化
        self.item_coin_value = 0.0  # 初始為 0，將根據文件加載或用戶輸入設置
        self.exchange_rates = {"chaos": 1.0, "divine": 1.0}  # 初始化匯率

        # 排序相關變數
        self.sort_column = None
        self.sort_reverse = False

        # 設定 UI
        self.setup_ui()
        self.load_items_from_file()
   
    def update_profits(self):
        """更新每個物品的利潤數據，根據新的 DC 比率，同時更新可購買數量"""
        item_coin_value = float(self.entry_item_coin_value.get()) if self.entry_item_coin_value.get() else 0.0
        if item_coin_value > 0:
            self.item_coin_value = item_coin_value  # 更新類別變數中的金幣值
        for item in self.items:
            ItemCalculator.calculate_profit(item, self.current_chaos, self.dc_ratio, self.item_coin_value)

        # 更新 TreeView 顯示
        self.update_treeview()

    def load_items_from_file(self):
        """從文件中加載物品資料並檢查數據類型"""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items = data.get("items", [])
                    self.current_chaos = float(data.get("current_chaos", 0.0))
                    self.dc_ratio = float(data.get("dc_ratio", 1.0))
                    self.item_coin_value = float(data.get("item_coin_value", 0.0))

                    # 初始化缺失的鍵
                    for item in self.items:
                        item.setdefault('extra_coin', 0.0)
                        item.setdefault('profit_c_to_c', 0.0)
                        item.setdefault('profit_c_to_d', 0.0)
                        item.setdefault('purchasable_with_chaos', 0)
                        item.setdefault('receive_coin', 0.0)
                        item.setdefault('sell_coin', 0.0)
                        item.setdefault('avg_coin_c', 0.0)
                        item.setdefault('sell_div_coin', 0.0)
                        item.setdefault('avg_coin_d', 0.0)
                        item.setdefault('avg_coin_d_extra', 0.0)
                        item.setdefault('total_profit_c_to_c', 0.0)
                        item.setdefault('total_profit_c_to_d', 0.0)

                        # 初始化可購買數量
                        if 'purchasable_with_chaos' not in item or item['purchasable_with_chaos'] == 0:
                            item['purchasable_with_chaos'] = int(self.current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0

                # 載入數據後重新計算每個物品的利潤
                self.update_profits()

                # 載入並更新 TreeView 顯示
                self.update_treeview()

            except (ValueError, json.JSONDecodeError) as e:
                messagebox.showerror("錯誤", f"讀取歷史紀錄時發生錯誤: {e}")

    def save_items_to_file(self):
        """將物品資料保存到文件，並確保數據類型正確"""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "items": self.items,
                    "current_chaos": float(self.current_chaos),
                    "dc_ratio": float(self.dc_ratio),
                    "item_coin_value": float(self.item_coin_value)  # 保存 item_coin_value
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"保存數據時發生錯誤: {e}")

    def on_treeview_click(self, event):
        """當點擊 TreeView 時，檢查是否點擊空白區域並取消選擇"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "nothing":
            self.tree.selection_remove(self.tree.selection())

    def edit_single_column(self, event):
        """處理欄位的單項編輯"""
        selected = self.tree.selection()
        if not selected:
            return

        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if not row:
            return

        selected_item_id = selected[0]
        selected_index = self.tree.index(selected_item_id)
        selected_item = self.items[selected_index]

        column_mapping = {
            "#2": "receive_price",
            "#3": "sell_price",
            "#4": "divine_sell_price",
            "#7": "purchasable_with_chaos"  # 添加購買數量的列
        }

        if column in column_mapping:
            field_name = column_mapping[column]
            current_value = selected_item.get(field_name, 0.0)

            new_value_str = simpledialog.askstring(
                "修改數值", f"請輸入新的 {field_name} 值 (目前: {current_value}):", initialvalue=str(current_value), parent=self.root
            )

            if new_value_str is not None:
                try:
                    # 嘗試解析為浮點數或分數
                    if '/' in new_value_str:
                        # 將分數轉換為浮點數
                        numerator, denominator = map(float, new_value_str.split('/'))
                        new_value = numerator / denominator
                    else:
                        new_value = float(new_value_str)

                    # 如果是 "purchasable_with_chaos"，要檢查數量是否超過倉庫混沌石數量
                    if field_name == "purchasable_with_chaos":
                        max_purchasable = int(self.current_chaos // selected_item['receive_price'])
                        if new_value > max_purchasable:
                            messagebox.showerror("錯誤", f"購買數量不能超過可用的混沌石數量 ({max_purchasable})。")
                            return


                    # 更新物品中的數值
                    self.items[selected_index][field_name] = new_value

                    # 更新利潤計算
                    self.update_profits()

                    # 更新顯示，確保最新數值被顯示
                    self.update_treeview()

                    # 保存到文件
                    self.save_items_to_file()

                except ValueError:
                    messagebox.showerror("錯誤", "請輸入有效的數字。")
        else:
            messagebox.showinfo("提示", "此欄位無法進行修改。")


    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 當前神聖石匯率
        self.exchange_rate_label = ttk.Label(main_frame, text=f"當前神聖石匯率 (C/D): {self.dc_ratio}")
        self.exchange_rate_label.grid(row=0, column=2, padx=10, pady=2, sticky=tk.E)

        update_exchange_rate_button = ttk.Button(main_frame, text="手動修改DC比率", command=self.manual_update_dc_ratio)
        update_exchange_rate_button.grid(row=0, column=3, padx=5, pady=2)

        # 單位物品價值 (金幣) 輸入框
        ttk.Label(main_frame, text="單位物品價值 (金幣):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entry_item_coin_value = ttk.Entry(main_frame, width=25)
        self.entry_item_coin_value.grid(row=5, column=1, pady=2)
        self.entry_item_coin_value.insert(0, str(self.item_coin_value))  # 加載並顯示上次保存的金幣值

        # 倉庫混沌石數量
        self.chaos_quantity_label = ttk.Label(main_frame, text=f"倉庫混沌石數量: {int(self.current_chaos // 1)}")
        self.chaos_quantity_label.grid(row=1, column=2, padx=10, pady=2, sticky=tk.E)
        chaos_button = ttk.Button(main_frame, text="修改混沌石數量", command=self.update_chaos_resources)
        chaos_button.grid(row=1, column=3, padx=5, pady=2)

        # 物品名稱
        ttk.Label(main_frame, text="物品名稱:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_item_name = ttk.Entry(main_frame, width=25)
        self.entry_item_name.grid(row=0, column=1, pady=2)

        # 混沌石購買價格
        ttk.Label(main_frame, text="混沌石購買價格:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_receive_price = ttk.Entry(main_frame, width=25)
        self.entry_receive_price.grid(row=1, column=1, pady=2)

        # 混沌石販賣價格
        ttk.Label(main_frame, text="混沌石販賣價格:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_sell_price.grid(row=2, column=1, pady=2)

        # 神聖石販賣價格
        ttk.Label(main_frame, text="神聖石販賣價格:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_divine_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_divine_sell_price.grid(row=3, column=1, pady=2)

        # 計算按鈕
        calculate_button = ttk.Button(main_frame, text="計算", command=self.calculate_profit)
        calculate_button.grid(row=6, column=0, columnspan=2, pady=10)


        # TreeView 表格
        columns = (
            "物品名稱", "C:物品", "物品:C",
            "物品:D", "C買C賣單利潤", "C買D賣單利潤",
            "C可購買數量", "所需C", "C買C賣總利潤", "C買D賣總利潤",
            "C買C賣平均金幣", "C買D賣平均金幣", "D換C額外平均金幣"
        )

        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        self.tree.grid(row=7, column=0, columnspan=4, sticky='nsew')

        self.tree.bind("<Button-1>", self.on_treeview_click)

        # 設置每個欄位的標題和寬度
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)

        # 添加滾動條
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=7, column=4, sticky="ns")

        # 移到程式下方的按鈕
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 刪除按鈕
        delete_button = ttk.Button(button_frame, text="刪除選中紀錄", command=self.delete_item)
        delete_button.grid(row=0, column=0, padx=5, pady=5)

        # 匯出 CSV 按鈕
        export_button = ttk.Button(button_frame, text="匯出為 CSV", command=self.export_to_csv)
        export_button.grid(row=0, column=1, padx=5, pady=5)

        self.tree.bind("<Double-1>", self.edit_single_column)

    def manual_update_dc_ratio(self):
        """手動輸入並更新 DC 比率"""
        try:
            new_dc_ratio_str = simpledialog.askstring("輸入 DC 比率", "請輸入新的神聖石對混沌石比率:", parent=self.root)
            if new_dc_ratio_str is None or new_dc_ratio_str.strip() == "":
                return
            new_dc_ratio_str = new_dc_ratio_str.strip()
            if not re.match(r'^\d+(\.\d+)?$', new_dc_ratio_str):
                raise ValueError("輸入的值不是有效的數字")
            new_dc_ratio = float(new_dc_ratio_str)
            self.dc_ratio = new_dc_ratio
            self.exchange_rate_label.config(text=f"當前神聖石匯率 (C/D): {self.dc_ratio:.2f}")
            self.update_profits()
            self.update_treeview()
            self.save_items_to_file()
        except ValueError as e:
            messagebox.showerror("錯誤", f"請輸入有效的數字（例如: 1.23 或 145）。\n錯誤訊息: {e}")

    def update_treeview(self):
        """更新 TreeView 中顯示的資料，並根據總利潤高亮"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.items:
            total_profit_c_to_c = item.get('total_profit_c_to_c', 0.0)
            total_profit_c_to_d = item.get('total_profit_c_to_d', 0.0)

            tag = "normal"
            if total_profit_c_to_c > 2000 or total_profit_c_to_d > 2000:
                tag = "highlight_2000C"
            elif total_profit_c_to_c > 1000 or total_profit_c_to_d > 1000:
                tag = "highlight_1000C"

            self.tree.insert('', 'end', values=(
                item['item_name'],
                f"{item['receive_price']:.2f}",
                f"{item['sell_price']:.2f}",
                f"{item['divine_sell_price']:.2f}",
                f"{item['profit_c_to_c']:.2f}",
                f"{item['profit_c_to_d']:.2f}",
                item['purchasable_with_chaos'],
                f"{item['required_chaos']:.2f}",  # 新增的「所需C」欄位
                f"{item['total_profit_c_to_c']:.2f}",
                f"{item['total_profit_c_to_d']:.2f}",
                f"{item['avg_coin_c']:.2f}" if isinstance(item['avg_coin_c'], (int, float)) else item['avg_coin_c'],
                f"{item['avg_coin_d']:.2f}" if isinstance(item['avg_coin_d'], (int, float)) else item['avg_coin_d'],
                f"{item['avg_coin_d_extra']:.2f}" if isinstance(item['avg_coin_d_extra'], (int, float)) else item['avg_coin_d_extra']
            ), tags=(tag,))

        self.tree.tag_configure("highlight_2000C", background="green")
        self.tree.tag_configure("highlight_1000C", background="yellow")
        self.tree.tag_configure("normal", background="white")

    def calculate_profit(self):
        """計算利潤並添加物品記錄"""
        try:
            receive_price = float(self.entry_receive_price.get())
            sell_price = float(self.entry_sell_price.get())
            # 對神聖石販賣價格進行特殊處理
            divine_sell_price_str = self.entry_divine_sell_price.get()
            if '/' in divine_sell_price_str:
                # 使用 Fraction 解析分數格式
                divine_sell_price = float(Fraction(divine_sell_price_str))
            else:
                divine_sell_price = float(divine_sell_price_str)

            item_coin_value = float(self.entry_item_coin_value.get())
            if item_coin_value > 0:
                self.item_coin_value = item_coin_value  # 更新類別變數中的金幣值
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字")
            return

        # 利潤和金幣消耗計算邏輯
        item_data = {
            "item_name": self.entry_item_name.get(),
            "receive_price": receive_price,
            "sell_price": sell_price,
            "divine_sell_price": divine_sell_price
        }

        # 計算利潤
        ItemCalculator.calculate_profit(item_data, self.current_chaos, self.dc_ratio, self.item_coin_value)

        # 插入到 TreeView
        self.tree.insert('', 'end', values=(
            item_data['item_name'],
            f"{item_data['receive_price']:.2f}",
            f"{item_data['sell_price']:.2f}",
            f"{item_data['divine_sell_price']:.2f}",
            f"{item_data['profit_c_to_c']:.2f}",  # 使用 profit_c_to_c
            f"{item_data['profit_c_to_d']:.2f}",  # 使用 profit_c_to_d
            item_data['purchasable_with_chaos'],
            f"{item_data['required_chaos']:.2f}",
            f"{item_data['total_profit_c_to_c']:.2f}",
            f"{item_data['total_profit_c_to_d']:.2f}",
            f"{item_data['avg_coin_c']:.2f}" if isinstance(item_data['avg_coin_c'], (int, float)) else item_data['avg_coin_c'],
            f"{item_data['avg_coin_d']:.2f}" if isinstance(item_data['avg_coin_d'], (int, float)) else item_data['avg_coin_d'],
            f"{item_data['avg_coin_d_extra']:.2f}" if isinstance(item_data['avg_coin_d_extra'], (int, float)) else item_data['avg_coin_d_extra']
        ))

        # 將 item_data 添加到 self.items 列表中
        self.items.append(item_data)

        # 保存並更新顯示
        self.save_items_to_file()
        self.update_treeview()
        self.clear_inputs()

    def clear_inputs(self):
        """清除輸入框"""
        self.entry_item_name.delete(0, tk.END)
        self.entry_receive_price.delete(0, tk.END)
        self.entry_sell_price.delete(0, tk.END)
        self.entry_divine_sell_price.delete(0, tk.END)
        self.entry_item_coin_value.delete(0, tk.END)

    def update_chaos_resources(self):
        """修改倉庫混沌石數量"""
        try:
            new_chaos_str = simpledialog.askstring("輸入混沌石數量", "請輸入目前混沌石數量:", parent=self.root)
            if new_chaos_str is None or new_chaos_str.strip() == "":
                return
            new_chaos_str = new_chaos_str.strip()
            if not re.match(r'^\d+(\.\d+)?$', new_chaos_str):
                raise ValueError("輸入的值不是有效的數字")
            new_chaos_value = float(new_chaos_str)
            self.current_chaos = new_chaos_value
            self.chaos_quantity_label.config(text=f"倉庫混沌石數量: {int(self.current_chaos)}")
            self.update_profits()
            self.update_treeview()
            self.save_items_to_file()
        except ValueError as e:
            messagebox.showerror("錯誤", f"請輸入有效的數字（例如: 100 或 100.5）。\n錯誤訊息: {e}")

    def delete_item(self):
        """刪除選中的物品記錄"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("錯誤", "請選擇要刪除的紀錄。")
            return

        selected_item_id = selected[0]
        selected_index = self.tree.index(selected_item_id)
        del self.items[selected_index]

        self.tree.delete(selected_item_id)
        self.save_items_to_file()

        messagebox.showinfo("成功", "已成功刪除選中的紀錄。")

    def export_to_csv(self):
        """將物品資料匯出為 CSV"""
        export_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not export_file_path:
            return
        try:
            with open(export_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    "item_name", "receive_price", "sell_price",
                    "divine_sell_price", "profit_c_to_c", "profit_c_to_d",
                    "purchasable_with_chaos", "receive_coin", "sell_coin", "sell_div_coin", "dc_coin"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.items:
                    writer.writerow({
                        "item_name": item.get('item_name', ''),
                        "receive_price": item.get('receive_price', 0.0),
                        "sell_price": item.get('sell_price', 0.0),
                        "divine_sell_price": item.get('divine_sell_price', 0.0),
                        "profit_c_to_c": item.get('profit_c_to_c', 0.0),
                        "profit_c_to_d": item.get('profit_c_to_d', 0.0),
                        "purchasable_with_chaos": item.get('purchasable_with_chaos', 0),
                        "receive_coin": item.get('receive_coin', 0.0),
                        "sell_coin": item.get('sell_coin', 0.0),
                        "sell_div_coin": item.get('sell_div_coin', 0.0),
                        "dc_coin": item.get('dc_coin', 0.0)
                    })
            messagebox.showinfo("導出成功", "歷史紀錄已成功導出為 CSV 文件。")
        except Exception as e:
            messagebox.showerror("錯誤", f"導出 CSV 文件時發生錯誤: {e}")


# 主程式執行
if __name__ == "__main__":
    root = tk.Tk()
    app = ItemManagerApp(root)
    root.mainloop()