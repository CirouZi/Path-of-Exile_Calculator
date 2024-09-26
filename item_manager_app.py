import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import json
import os
import csv


class ItemManagerApp:
    DATA_FILE = "items_data.json"

    def __init__(self, root):
        self.root = root
        self.root.title("交易計算器")

        # 初始化變數
        self.items = []
        self.current_chaos = 0.0
        self.current_divine = 0.0
        self.dc_ratio = 1.0

        # 設定 UI
        self.setup_ui()
        self.load_items_from_file()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        columns = (
            "item_name", "receive_price", "sell_price",
            "divine_buy_price", "divine_sell_price",
            "profit_c_to_c", "profit_c_to_d",
            "purchasable_with_chaos", "purchasable_with_divine"
        )

        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        self.tree.grid(row=7, column=0, columnspan=4, sticky='nsew')

        # 設定 Treeview 的標題及欄位
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").capitalize())
            self.tree.column(col, anchor=tk.CENTER)

        # 雙擊進行欄位修改
        self.tree.bind("<Double-1>", self.edit_single_column)

        # 顯示 DC 比率
        self.dc_ratio_label = ttk.Label(main_frame, text=f"DC 比率: {self.dc_ratio}")
        self.dc_ratio_label.grid(row=0, column=2, padx=10, pady=2, sticky=tk.E)
        update_dc_button = ttk.Button(main_frame, text="修改 DC 比率", command=self.update_dc_ratio)
        update_dc_button.grid(row=0, column=3, padx=5, pady=2)

        # 混沌石及修改按鈕
        self.chaos_quantity_label = ttk.Label(main_frame, text=f"倉庫混沌石數量: {int(self.current_chaos // 1)}")
        self.chaos_quantity_label.grid(row=1, column=2, padx=10, pady=2, sticky=tk.E)
        chaos_button = ttk.Button(main_frame, text="修改混沌石數量", command=self.update_chaos_resources)
        chaos_button.grid(row=1, column=3, padx=5, pady=2)

        # 神聖石及修改按鈕
        self.divine_quantity_label = ttk.Label(main_frame, text=f"倉庫神聖石數量: {int(self.current_divine)}")
        self.divine_quantity_label.grid(row=2, column=2, padx=10, pady=2, sticky=tk.E)
        divine_button = ttk.Button(main_frame, text="修改神聖石數量", command=self.update_divine_resources)
        divine_button.grid(row=2, column=3, padx=5, pady=2)

        # 添加物品的輸入欄位
        ttk.Label(main_frame, text="物品名稱:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_item_name = ttk.Entry(main_frame, width=25)
        self.entry_item_name.grid(row=0, column=1, pady=2)

        ttk.Label(main_frame, text="混沌石購買價格:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_receive_price = ttk.Entry(main_frame, width=25)
        self.entry_receive_price.grid(row=1, column=1, pady=2)

        ttk.Label(main_frame, text="混沌石販賣價格:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_sell_price.grid(row=2, column=1, pady=2)

        ttk.Label(main_frame, text="神聖石購買價格:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_divine_buy_price = ttk.Entry(main_frame, width=25)
        self.entry_divine_buy_price.grid(row=3, column=1, pady=2)

        ttk.Label(main_frame, text="神聖石販賣價格:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entry_divine_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_divine_sell_price.grid(row=4, column=1, pady=2)

        ttk.Label(main_frame, text="單位物品價值 (金幣):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entry_item_coin_value = ttk.Entry(main_frame, width=25)
        self.entry_item_coin_value.grid(row=5, column=1, pady=2)

        # 計算按鈕
        calculate_button = ttk.Button(main_frame, text="計算", command=self.calculate_profit)
        calculate_button.grid(row=6, column=0, columnspan=2, pady=10)

        # 刪除按鈕
        delete_button = ttk.Button(main_frame, text="刪除選中紀錄", command=self.delete_item)
        delete_button.grid(row=8, column=0, columnspan=2, pady=5)

        # 匯出 CSV 按鈕
        export_button = ttk.Button(main_frame, text="匯出為 CSV", command=self.export_to_csv)
        export_button.grid(row=9, column=0, columnspan=2, pady=5)

    def load_items_from_file(self):
        """從文件中加載物品資料"""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items = data.get("items", [])
                    self.current_chaos = data.get("current_chaos", 0.0)
                    self.current_divine = data.get("current_divine", 0.0)
                    self.dc_ratio = data.get("dc_ratio", 1.0)
                    for item in self.items:
                        self.display_item_in_treeview(item)
            except Exception as e:
                messagebox.showerror("錯誤", f"讀取歷史紀錄時發生錯誤: {e}")

    def save_items_to_file(self):
        """將物品資料保存到文件"""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "items": self.items,
                    "current_chaos": self.current_chaos,
                    "current_divine": self.current_divine,
                    "dc_ratio": self.dc_ratio
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"保存數據時發生錯誤: {e}")

    def display_item_in_treeview(self, item_data):
        """顯示物品在 TreeView 中"""
        self.tree.insert('', 'end', values=(
            item_data.get('item_name', ''),
            f"{item_data.get('receive_price', 0.0):.2f}",
            f"{item_data.get('sell_price', 0.0):.2f}",
            f"{item_data.get('divine_buy_price', 0.0):.2f}",
            f"{item_data.get('divine_sell_price', 0.0):.2f}",
            f"{item_data.get('profit_c_to_c', 0.0):.2f}",
            f"{item_data.get('profit_c_to_d', 0.0):.2f}",
            item_data.get('purchasable_with_chaos', 0),
            item_data.get('purchasable_with_divine', 0)
        ))

    def update_treeview(self):
        """更新 TreeView 中顯示的資料"""
        for index, item in enumerate(self.items):
            item['purchasable_with_chaos'] = int(self.current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0
            total_chaos_from_divine = self.current_divine * self.dc_ratio
            item['purchasable_with_divine'] = int(total_chaos_from_divine // item['receive_price']) if item['receive_price'] > 0 else 0
            self.tree.item(self.tree.get_children()[index], values=(
                item['item_name'],
                f"{item['receive_price']:.2f}",
                f"{item['sell_price']:.2f}",
                f"{item['divine_buy_price']:.2f}",
                f"{item['divine_sell_price']:.2f}",
                f"{item['profit_c_to_c']:.2f}",
                f"{item['profit_c_to_d']:.2f}",
                item['purchasable_with_chaos'],
                item['purchasable_with_divine']
            ))

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
            "#4": "divine_buy_price",
            "#5": "divine_sell_price"
        }

        if column in column_mapping:
            field_name = column_mapping[column]
            current_value = selected_item.get(field_name, 0.0)

            new_value_str = simpledialog.askstring(
                "修改數值", f"請輸入新的 {field_name} 值 (目前: {current_value}):", initialvalue=str(current_value), parent=self.root
            )

            if new_value_str is not None:
                try:
                    new_value = float(new_value_str)
                    self.items[selected_index][field_name] = new_value

                    profit_c_to_c = self.items[selected_index]['sell_price'] - self.items[selected_index]['receive_price']
                    profit_c_to_d = (self.items[selected_index]['divine_sell_price'] * self.dc_ratio) - self.items[selected_index]['receive_price']

                    self.items[selected_index]['profit_c_to_c'] = profit_c_to_c
                    self.items[selected_index]['profit_c_to_d'] = profit_c_to_d

                    self.update_treeview()
                    self.save_items_to_file()

                except ValueError:
                    messagebox.showerror("錯誤", "請確保輸入的是有效的數字或分數格式。")
        else:
            messagebox.showinfo("提示", "此欄位無法進行修改。")

    def calculate_profit(self):
        """計算利潤並添加物品記錄"""
        item_name = self.entry_item_name.get()

        try:
            receive_price = float(self.entry_receive_price.get())
            sell_price = float(self.entry_sell_price.get())
            divine_buy_price = float(self.entry_divine_buy_price.get())
            divine_sell_price = float(self.entry_divine_sell_price.get())
            item_coin_value = float(self.entry_item_coin_value.get())
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")
            return

        profit_c_to_c = sell_price - receive_price
        profit_c_to_d = (divine_sell_price * self.dc_ratio) - receive_price

        purchasable_with_chaos = int(self.current_chaos // receive_price) if receive_price > 0 else 0
        purchasable_with_divine = int((self.current_divine * self.dc_ratio) // receive_price) if receive_price > 0 else 0

        item_data = {
            "item_name": item_name,
            "receive_price": receive_price,
            "sell_price": sell_price,
            "divine_buy_price": divine_buy_price,
            "divine_sell_price": divine_sell_price,
            "dc_ratio": self.dc_ratio,
            "item_coin_value": item_coin_value,
            "profit_c_to_c": profit_c_to_c,
            "profit_c_to_d": profit_c_to_d,
            "purchasable_with_chaos": purchasable_with_chaos,
            "purchasable_with_divine": purchasable_with_divine
        }

        self.items.append(item_data)
        self.save_items_to_file()
        self.display_item_in_treeview(item_data)

        self.entry_item_name.delete(0, tk.END)
        self.entry_receive_price.delete(0, tk.END)
        self.entry_sell_price.delete(0, tk.END)
        self.entry_divine_buy_price.delete(0, tk.END)
        self.entry_divine_sell_price.delete(0, tk.END)
        self.entry_item_coin_value.delete(0, tk.END)

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

    def update_dc_ratio(self):
        """修改 DC 比率"""
        new_dc_ratio_str = simpledialog.askstring("修改 DC 比率", "請輸入新的 DC 比率:", parent=self.root)
        if new_dc_ratio_str is None:
            return
        try:
            new_dc_ratio = float(new_dc_ratio_str)
            self.dc_ratio = new_dc_ratio
            self.dc_ratio_label.config(text=f"DC 比率: {self.dc_ratio}")

            for item in self.items:
                profit_c_to_d = (item['divine_sell_price'] * self.dc_ratio) - item['receive_price']
                item['profit_c_to_d'] = profit_c_to_d

            self.update_treeview()
            self.save_items_to_file()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")

    def update_chaos_resources(self):
        """修改混沌石數量"""
        new_chaos_str = simpledialog.askstring("輸入混沌石數量", "請輸入目前混沌石數量:", parent=self.root)
        if new_chaos_str is None:
            return
        try:
            self.current_chaos = float(new_chaos_str)
            self.chaos_quantity_label.config(text=f"倉庫混沌石數量: {int(self.current_chaos // 1)}")
            self.save_items_to_file()
            self.update_treeview()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")

    def update_divine_resources(self):
        """修改神聖石數量"""
        new_divine_str = simpledialog.askstring("輸入神聖石數量", "請輸入目前神聖石數量:", parent=self.root)
        if new_divine_str is None:
            return
        try:
            self.current_divine = float(new_divine_str)
            self.divine_quantity_label.config(text=f"倉庫神聖石數量: {int(self.current_divine)}")
            self.save_items_to_file()
            self.update_treeview()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")

    def export_to_csv(self):
        """將物品資料匯出為 CSV"""
        export_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not export_file_path:
            return
        try:
            with open(export_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    "item_name", "receive_price", "sell_price", 
                    "divine_buy_price", "divine_sell_price", 
                    "profit_c_to_c", "profit_c_to_d", 
                    "purchasable_with_chaos", "purchasable_with_divine"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # 寫入 CSV 標頭
                writer.writeheader()

                # 寫入每個物品的數據
                for item in self.items:
                    writer.writerow({
                        "item_name": item.get('item_name', ''),
                        "receive_price": item.get('receive_price', 0.0),
                        "sell_price": item.get('sell_price', 0.0),
                        "divine_buy_price": item.get('divine_buy_price', 0.0),
                        "divine_sell_price": item.get('divine_sell_price', 0.0),
                        "profit_c_to_c": item.get('profit_c_to_c', 0.0),
                        "profit_c_to_d": item.get('profit_c_to_d', 0.0),
                        "purchasable_with_chaos": item.get('purchasable_with_chaos', 0),
                        "purchasable_with_divine": item.get('purchasable_with_divine', 0)
                    })

            messagebox.showinfo("導出成功", "歷史紀錄已成功導出為 CSV 文件。")
        except Exception as e:
            messagebox.showerror("錯誤", f"導出 CSV 文件時發生錯誤: {e}")


# 主程式執行
if __name__ == "__main__":
    root = tk.Tk()
    app = ItemManagerApp(root)
    root.mainloop()
