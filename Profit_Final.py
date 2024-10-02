import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import json
import os
import csv
from typing import List, Dict


class ItemManagerApp:
    DATA_FILE = "items_data.json"

    def __init__(self, root):
        self.root = root
        self.root.title("交易計算器")

        # 初始化變數
        self.items: List[Dict] = []
        self.current_chaos = 0.0
        self.current_divine = 0.0
        self.dc_ratio = 1.0
        self.exchange_rates = {"chaos": 1.0, "divine": 1.0}  # 初始化匯率

        # 排序相關變數
        self.sort_column = None
        self.sort_reverse = False

        # 設定 UI
        self.setup_ui()
        self.load_items_from_file()

    def calculate_profit_for_item(self, item: Dict):
        """計算單個物品的利潤、總利潤和可購買數量"""
        # 計算單個利潤
        item['profit_c_to_c'] = item['sell_price'] - item['receive_price']
        item['profit_c_to_d'] = (item['divine_sell_price'] * self.dc_ratio) - item['receive_price']
    
        # 計算可購買數量
        item['purchasable_with_chaos'] = int(self.current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0
        total_chaos_from_divine = self.current_divine * self.dc_ratio
        item['purchasable_with_divine'] = int(total_chaos_from_divine // item['receive_price']) if item['receive_price'] > 0 else 0
    
        # 計算總利潤（取混沌石或神聖石能買的最大數量來計算）
        max_purchasable = max(item['purchasable_with_chaos'], item['purchasable_with_divine'])
        item['total_profit_c_to_c'] = item['profit_c_to_c'] * max_purchasable
        item['total_profit_c_to_d'] = item['profit_c_to_d'] * max_purchasable

    def update_profits(self):
        """更新每個物品的利潤數據，根據新的 DC 比率，同時更新可購買數量"""
        for item in self.items:
            self.calculate_profit_for_item(item)

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

    def on_treeview_click(self, event):
        """當點擊 TreeView 時，檢查是否點擊空白區域並取消選擇"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "nothing":
            self.tree.selection_remove(self.tree.selection())

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.exchange_rate_label = ttk.Label(main_frame, text=f"當前神聖石匯率 (C/D): {self.dc_ratio}")
        self.exchange_rate_label.grid(row=0, column=2, padx=10, pady=2, sticky=tk.E)

        update_exchange_rate_button = ttk.Button(main_frame, text="手動修改DC比率", command=self.manual_update_dc_ratio)
        update_exchange_rate_button.grid(row=0, column=3, padx=5, pady=2)

        columns = (
            "item_name", "receive_price", "sell_price",
            "divine_sell_price", "profit_c_to_c", "profit_c_to_d",
            "purchasable_with_chaos", "purchasable_with_divine", "total_profit_c_to_c", "total_profit_c_to_d"
        )

        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        self.tree.grid(row=7, column=0, columnspan=4, sticky='nsew')

        self.tree.bind("<Button-1>", self.on_treeview_click)

        

        # 設置每個欄位的標題和適當的寬度
        self.tree.heading("item_name", text="Item Name")
        self.tree.column("item_name", anchor=tk.CENTER, width=150)

        self.tree.heading("receive_price", text="Receive Price")
        self.tree.column("receive_price", anchor=tk.CENTER, width=100)

        self.tree.heading("sell_price", text="Sell Price")
        self.tree.column("sell_price", anchor=tk.CENTER, width=80)

        self.tree.heading("divine_sell_price", text="Divine Sell Price")
        self.tree.column("divine_sell_price", anchor=tk.CENTER, width=100)

        self.tree.heading("profit_c_to_c", text="Profit C to C")
        self.tree.column("profit_c_to_c", anchor=tk.CENTER, width=100)

        self.tree.heading("profit_c_to_d", text="Profit C to D")
        self.tree.column("profit_c_to_d", anchor=tk.CENTER, width=100)

        self.tree.heading("purchasable_with_chaos", text="Purchasable with Chaos")
        self.tree.column("purchasable_with_chaos", anchor=tk.CENTER, width=150)

        self.tree.heading("purchasable_with_divine", text="Purchasable with Divine")
        self.tree.column("purchasable_with_divine", anchor=tk.CENTER, width=150)

        self.tree.heading("total_profit_c_to_c", text="Total Profit C to C")
        self.tree.column("total_profit_c_to_c", anchor=tk.CENTER, width=150)

        self.tree.heading("total_profit_c_to_d", text="Total Profit C to D")
        self.tree.column("total_profit_c_to_d", anchor=tk.CENTER, width=150)

        self.tree.bind("<Double-1>", self.edit_single_column)

        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').capitalize(), command=lambda _col=col: self.sort_treeview(_col))

        self.chaos_quantity_label = ttk.Label(main_frame, text=f"倉庫混沌石數量: {int(self.current_chaos // 1)}")
        self.chaos_quantity_label.grid(row=1, column=2, padx=10, pady=2, sticky=tk.E)
        chaos_button = ttk.Button(main_frame, text="修改混沌石數量", command=self.update_chaos_resources)
        chaos_button.grid(row=1, column=3, padx=5, pady=2)

        self.divine_quantity_label = ttk.Label(main_frame, text=f"倉庫神聖石數量: {int(self.current_divine)}")
        self.divine_quantity_label.grid(row=2, column=2, padx=10, pady=2, sticky=tk.E)
        divine_button = ttk.Button(main_frame, text="修改神聖石數量", command=self.update_divine_resources)
        divine_button.grid(row=2, column=3, padx=5, pady=2)

        ttk.Label(main_frame, text="物品名稱:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_item_name = ttk.Entry(main_frame, width=25)
        self.entry_item_name.grid(row=0, column=1, pady=2)

        ttk.Label(main_frame, text="混沌石購買價格:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_receive_price = ttk.Entry(main_frame, width=25)
        self.entry_receive_price.grid(row=1, column=1, pady=2)

        ttk.Label(main_frame, text="混沌石販賣價格:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_sell_price.grid(row=2, column=1, pady=2)

        ttk.Label(main_frame, text="神聖石販賣價格:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_divine_sell_price = ttk.Entry(main_frame, width=25)
        self.entry_divine_sell_price.grid(row=3, column=1, pady=2)

        calculate_button = ttk.Button(main_frame, text="計算", command=self.calculate_profit)
        calculate_button.grid(row=6, column=0, columnspan=2, pady=10)

        delete_button = ttk.Button(main_frame, text="刪除選中紀錄", command=self.delete_item)
        delete_button.grid(row=8, column=0, columnspan=2, pady=5)

        export_button = ttk.Button(main_frame, text="匯出為 CSV", command=self.export_to_csv)
        export_button.grid(row=9, column=0, columnspan=2, pady=5)

    def sort_treeview(self, col):
        """根據指定的欄位排序 TreeView 資料"""
        self.sort_reverse = not self.sort_reverse if self.sort_column == col else False
        self.sort_column = col

        # 對資料進行排序
        self.items.sort(key=lambda x: x[col], reverse=self.sort_reverse)
        self.update_treeview()

    def manual_update_dc_ratio(self):
        """手動輸入並更新 DC 比率"""
        try:
            new_dc_ratio_str = simpledialog.askstring("輸入 DC 比率", "請輸入新的神聖石對混沌石比率:", parent=self.root)
            if new_dc_ratio_str is None:
                return
            self.dc_ratio = float(new_dc_ratio_str)

            # 更新 UI 中顯示的 DC 比率
            self.exchange_rate_label.config(text=f"當前神聖石匯率 (C/D): {self.dc_ratio:.2f}")

            # 重新計算利潤
            self.update_profits()
            self.update_treeview()

            # 保存更新到文件
            self.save_items_to_file()

        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")

    def update_treeview(self):
        """更新 TreeView 中顯示的資料，並根據總利潤高亮"""
        # 首先清空 TreeView 中的所有條目
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
                item['purchasable_with_divine'],
                f"{total_profit_c_to_c:.2f}",
                f"{total_profit_c_to_d:.2f}"
            ), tags=(tag,))

        self.tree.tag_configure("highlight_2000C", background="green")
        self.tree.tag_configure("highlight_1000C", background="yellow")
        self.tree.tag_configure("normal", background="white")

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
            "#4": "divine_sell_price"
        }

        if column in column_mapping:
            field_name = column_mapping[column]
            current_value = selected_item.get(field_name, 0.0)

            new_value_str = simpledialog.askstring(
                "修改數值", f"請輸入新的 {field_name} 值 (目前: {current_value}):", initialvalue=str(current_value), parent=self.root
            )

            if new_value_str is not None:
                try:
                    new_value = float(eval(new_value_str))
                    self.items[selected_index][field_name] = new_value

                    # 更新利潤計算
                    self.calculate_profit_for_item(self.items[selected_index])
                    self.update_treeview_row(selected_index)
                    self.save_items_to_file()

                except (ValueError, SyntaxError):
                    messagebox.showerror("錯誤", "請確保輸入的是有效的數字或數學表達式。")
        else:
            messagebox.showinfo("提示", "此欄位無法進行修改。")

    def update_treeview_row(self, item_index):
        """僅更新指定行的數據"""
        item = self.items[item_index]
        self.tree.item(self.tree.get_children()[item_index], values=(
            item['item_name'],
            f"{item['receive_price']:.2f}",
            f"{item['sell_price']:.2f}",
            f"{item['divine_sell_price']:.2f}",
            f"{item['profit_c_to_c']:.2f}",
            f"{item['profit_c_to_d']:.2f}",
            item['purchasable_with_chaos'],
            item['purchasable_with_divine'],
            f"{item['total_profit_c_to_c']:.2f}",
            f"{item['total_profit_c_to_d']:.2f}"
        ))

    def calculate_profit(self):
        """計算利潤並添加物品記錄"""
        item_name = self.entry_item_name.get()

        try:
            # 使用 eval 來處理數學表達式，確保即使用戶輸入 1/1.16 也能正確解析
            receive_price = float(eval(self.entry_receive_price.get()))
            sell_price = float(eval(self.entry_sell_price.get()))
            divine_sell_price = float(eval(self.entry_divine_sell_price.get()))
        except (ValueError, SyntaxError):
            messagebox.showerror("錯誤", "請輸入有效的數字或數學表達式。")
            return

        # 利潤計算
        profit_c_to_c = sell_price - receive_price
        profit_c_to_d = (divine_sell_price * self.dc_ratio) - receive_price

        # 可購買數量計算
        purchasable_with_chaos = int(self.current_chaos // receive_price) if receive_price > 0 else 0
        purchasable_with_divine = int((self.current_divine * self.dc_ratio) // receive_price) if receive_price > 0 else 0

        # 總利潤計算
        max_purchasable = max(purchasable_with_chaos, purchasable_with_divine)
        total_profit_c_to_c = profit_c_to_c * max_purchasable if max_purchasable > 0 else 0.0
        total_profit_c_to_d = profit_c_to_d * max_purchasable if max_purchasable > 0 else 0.0

        # 創建物品資料結構
        item_data = {
            "item_name": item_name,
            "receive_price": receive_price,
            "sell_price": sell_price,
            "divine_sell_price": divine_sell_price,
            "dc_ratio": self.dc_ratio,
            "profit_c_to_c": profit_c_to_c,
            "profit_c_to_d": profit_c_to_d,
            "purchasable_with_chaos": purchasable_with_chaos,
            "purchasable_with_divine": purchasable_with_divine,
            "total_profit_c_to_c": total_profit_c_to_c,
            "total_profit_c_to_d": total_profit_c_to_d
        }

        # 將物品添加到列表中
        self.items.append(item_data)

        # 保存到文件
        self.save_items_to_file()

        # 確保 TreeView 更新顯示數據
        self.update_treeview()

        # 清除輸入框
        self.entry_item_name.delete(0, tk.END)
        self.entry_receive_price.delete(0, tk.END)
        self.entry_sell_price.delete(0, tk.END)
        self.entry_divine_sell_price.delete(0, tk.END)
        
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

    def update_chaos_resources(self):
        """修改倉庫混沌石數量"""
        try:
            new_chaos_str = simpledialog.askstring("輸入混沌石數量", "請輸入目前混沌石數量:", parent=self.root)
            if new_chaos_str is None:
                return
            self.current_chaos = float(new_chaos_str)
            self.chaos_quantity_label.config(text=f"倉庫混沌石數量: {int(self.current_chaos // 1)}")
            self.update_profits()
            self.update_treeview()
            self.save_items_to_file()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字。")

    def update_divine_resources(self):
        """修改倉庫神聖石數量"""
        try:
            new_divine_str = simpledialog.askstring("輸入神聖石數量", "請輸入目前神聖石數量:", parent=self.root)
            if new_divine_str is None:
                return
            self.current_divine = float(new_divine_str)
            self.divine_quantity_label.config(text=f"倉庫神聖石數量: {int(self.current_divine)}")
            self.update_profits()
            self.update_treeview()
            self.save_items_to_file()
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
                    "divine_sell_price", "profit_c_to_c", "profit_c_to_d",
                    "purchasable_with_chaos", "purchasable_with_divine"
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
