import tkinter as tk
from tkinter import messagebox, ttk, END, simpledialog, filedialog
import json
import os
import csv

# 文件名常量
DATA_FILE = "items_data.json"
items = []
current_chaos = 0.0  # 初始混沌石數量
current_divine = 0.0  # 初始神聖石數量
dc_ratio = 1.0  # DC 比率，預設為 1
tree = None  # 全局變數
root = None  # 定義全局的 root 變數

# 解析分數或數值輸入
def parse_fractional_input(value_str):
    try:
        if '/' in value_str:
            numerator, denominator = value_str.split('/')
            return float(numerator) / float(denominator)
        else:
            return float(value_str)
    except ValueError:
        raise ValueError("輸入錯誤，無法解析為有效數字")

# 加載保存的數據
def load_items_from_file():
    global items, current_chaos, current_divine, dc_ratio
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("items", [])
                current_chaos = data.get("current_chaos", 0.0)
                current_divine = data.get("current_divine", 0.0)
                dc_ratio = data.get("dc_ratio", 1.0)
                # 確保每個項目包含所有必要的鍵
                for item in items:
                    item.setdefault('divine_buy_price', 0.0)
                    item.setdefault('divine_sell_price', 0.0)
                    item.setdefault('profit_c_to_c', 0.0)
                    item.setdefault('profit_c_to_d', 0.0)
                    item.setdefault('purchasable_with_chaos', 0)  # 可購買混沌石數量
                    item.setdefault('purchasable_with_divine', 0)  # 可購買神聖石數量
                    item.setdefault('dc_ratio', 1.0)
                    item.setdefault('item_coin_value', 0.0)
        except json.JSONDecodeError:
            items = []
            messagebox.showwarning("警告", "歷史紀錄檔案格式錯誤，已重新建立。")
        except Exception as e:
            items = []
            messagebox.showerror("錯誤", f"讀取歷史紀錄時發生錯誤: {e}")

# 保存數據
def save_items_to_file():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "items": items, 
                "current_chaos": current_chaos, 
                "current_divine": current_divine,
                "dc_ratio": dc_ratio  # 保存DC比率
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("錯誤", f"保存數據時發生錯誤: {e}")

# 顯示在 Treeview 中的函數
def display_item_in_treeview(tree, item_data):
    # 確保每個條目有正確的數據顯示在 Treeview 中
    tree.insert('', 'end', values=(
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
    
# 更新TreeView中顯示的數據
def update_treeview():
    for index, item in enumerate(items):
        item['purchasable_with_chaos'] = int(current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0
        total_chaos_from_divine = current_divine * dc_ratio
        item['purchasable_with_divine'] = int(total_chaos_from_divine // item['receive_price']) if item['receive_price'] > 0 else 0
        tree.item(tree.get_children()[index], values=(
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

# 更新倉庫混沌石數量
def update_chaos_resources():
    global current_chaos, tree, items, root
    try:
        new_chaos_str = simpledialog.askstring("輸入混沌石數量", "請輸入目前混沌石數量:", parent=root)
        if new_chaos_str is None:
            return
        new_chaos = parse_fractional_input(new_chaos_str)
        current_chaos = new_chaos
        save_items_to_file()
        update_treeview()
        chaos_quantity_label.config(text=f"倉庫混沌石數量: {int(current_chaos // 1)}")
    except ValueError:
        messagebox.showerror("錯誤", "請確保輸入的是有效的數字或分數格式。")

# 更新倉庫神聖石數量
def update_divine_resources():
    global current_divine, tree, items, root
    try:
        new_divine_str = simpledialog.askstring("輸入神聖石數量", "請輸入目前神聖石數量:", parent=root)
        if new_divine_str is None:
            return
        new_divine = parse_fractional_input(new_divine_str)
        current_divine = new_divine
        save_items_to_file()
        update_treeview()
        divine_quantity_label.config(text=f"倉庫神聖石數量: {int(current_divine)}")
    except ValueError:
        messagebox.showerror("錯誤", "請確保輸入的是有效的數字或分數格式。")

def update_dc_ratio():
    global dc_ratio, tree, items, dc_ratio_label

    # 請求輸入新的 DC 比率
    new_dc_ratio_str = simpledialog.askstring("修改 DC 比率", "請輸入新的 DC 比率:", parent=root)
    if new_dc_ratio_str is None:
        return  # 如果用戶取消操作，則退出
    try:
        # 嘗試解析用戶輸入的值
        new_dc_ratio = parse_fractional_input(new_dc_ratio_str)
        dc_ratio = new_dc_ratio  # 更新全局的 DC 比率

        # 更新顯示的 DC 比率
        dc_ratio_label.config(text=f"DC 比率: {dc_ratio}")

        # 遍歷所有項目並重新計算與 DC 比率相關的數值，包括 C買D賣的利潤
        for item in items:
            # C買D賣邏輯： 神聖石販賣價格 * DC 比率 - 混沌石購買價格
            profit_c_to_d = (item['divine_sell_price'] * dc_ratio) - item['receive_price']
            item['profit_c_to_d'] = profit_c_to_d

        # 更新顯示的數據
        update_treeview()

        # 保存新的 DC 比率到文件
        save_items_to_file()
    except ValueError:
        messagebox.showerror("錯誤", "請確保輸入的是有效的數字或分數格式。")


def update_treeview():
    for index, item in enumerate(items):
        # 重新計算可購買數量
        item['purchasable_with_chaos'] = int(current_chaos // item['receive_price']) if item['receive_price'] > 0 else 0
        total_chaos_from_divine = current_divine * dc_ratio
        item['purchasable_with_divine'] = int(total_chaos_from_divine // item['receive_price']) if item['receive_price'] > 0 else 0

        # 更新 Treeview 中的顯示，包括 C買D賣的利潤
        tree.item(tree.get_children()[index], values=(
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


# 單欄修改功能
def edit_single_column(event):
    global tree, items, current_chaos, current_divine, dc_ratio, root  # 確保 root 可用
    selected = tree.selection()
    if not selected:
        return

    column = tree.identify_column(event.x)  # 獲取選中的欄位
    row = tree.identify_row(event.y)        # 獲取選中的行
    
    if not row:
        return

    selected_item_id = selected[0]
    selected_index = tree.index(selected_item_id)
    selected_item = items[selected_index]

    # 定義欄位對應
    column_mapping = {
        "#2": "receive_price",         # 混沌石購買價格
        "#3": "sell_price",            # 混沌石販賣價格
        "#4": "divine_buy_price",      # 神聖石購買價格
        "#5": "divine_sell_price"      # 神聖石販賣價格
    }

    if column in column_mapping:
        field_name = column_mapping[column]
        current_value = selected_item.get(field_name, 0.0)

         # 彈出對話框讓用戶修改
        new_value_str = simpledialog.askstring(
            "修改數值",
            f"請輸入新的 {field_name} 值 (目前: {current_value}):",
            initialvalue=str(current_value),
            parent=root
)

        if new_value_str is not None:
            try:
                new_value = parse_fractional_input(new_value_str) # 轉換為浮點數
                items[selected_index][field_name] = new_value # 更新數據

                # 重新計算利潤
                profit_c_to_c = items[selected_index]['sell_price'] - items[selected_index]['receive_price']

                # 正確的 C買D賣利潤計算邏輯： 神聖石販賣價格 * DC 比率 - 混沌石購買價格
                profit_c_to_d = (items[selected_index]['divine_sell_price'] * dc_ratio) - items[selected_index]['receive_price']
                
                items[selected_index]['profit_c_to_c'] = profit_c_to_c
                items[selected_index]['profit_c_to_d'] = profit_c_to_d

                # 更新 Treeview 中的顯示
                tree.item(selected_item_id, values=(
                    selected_item['item_name'],
                    f"{selected_item['receive_price']:.2f}",
                    f"{selected_item['sell_price']:.2f}",
                    f"{selected_item['divine_buy_price']:.2f}",
                    f"{selected_item['divine_sell_price']:.2f}",
                    f"{selected_item['profit_c_to_c']:.2f}",
                    f"{selected_item['profit_c_to_d']:.2f}",
                    selected_item['purchasable_with_chaos'],
                    selected_item['purchasable_with_divine']
                ))

                # 保存更新
                save_items_to_file()

            except ValueError:
                messagebox.showerror("錯誤", "請確保輸入的是有效的數字或分數格式。")
    else:
        messagebox.showinfo("提示", "此欄位無法進行修改。")

# 刪除選中的紀錄
def delete_item():
    global tree, items
    selected = tree.selection()
    if not selected:
        messagebox.showerror("錯誤", "請選擇要刪除的紀錄。")
        return

    selected_item_id = selected[0]
    selected_index = tree.index(selected_item_id)
    del items[selected_index]

    # 刪除 Treeview 中的項目
    tree.delete(selected_item_id)
    save_items_to_file()

# 計算並顯示利潤
def calculate_profit():
    global tree, items, current_chaos, current_divine, dc_ratio

    # 獲取輸入的數據
    item_name = entry_item_name.get()
    fields = {
        "混沌石購買價格": entry_receive_price.get(),
        "混沌石販賣價格": entry_sell_price.get(),
        "神聖石購買價格": entry_divine_buy_price.get(),
        "神聖石販賣價格": entry_divine_sell_price.get(),
        "單位物品價值 (金幣)": entry_item_coin_value.get()
    }

    try:
        receive_price = parse_fractional_input(fields["混沌石購買價格"])
    except ValueError:
        messagebox.showerror("錯誤", "混沌石購買價格輸入錯誤。")
        return

    try:
        sell_price = parse_fractional_input(fields["混沌石販賣價格"])
    except ValueError:
        messagebox.showerror("錯誤", "混沌石販賣價格輸入錯誤。")
        return

    try:
        divine_buy_price = parse_fractional_input(fields["神聖石購買價格"])
    except ValueError:
        messagebox.showerror("錯誤", "神聖石購買價格輸入錯誤。")
        return

    try:
        divine_sell_price = parse_fractional_input(fields["神聖石販賣價格"])
    except ValueError:
        messagebox.showerror("錯誤", "神聖石販賣價格輸入錯誤。")
        return

    try:
        item_coin_value = parse_fractional_input(fields["單位物品價值 (金幣)"])
    except ValueError:
        messagebox.showerror("錯誤", "單位物品價值輸入錯誤。")
        return

    # 使用全域 dc_ratio 計算 C 收 D 賣利潤
    profit_c_to_c = sell_price - receive_price
    profit_c_to_d = (divine_sell_price * dc_ratio) - receive_price

    # 計算可購買數量
    purchasable_with_chaos = int(current_chaos // receive_price) if receive_price > 0 else 0
    purchasable_with_divine = int((current_divine * dc_ratio) // receive_price) if receive_price > 0 else 0

    # 保存紀錄
    item_data = {
        "item_name": item_name,
        "receive_price": receive_price,
        "sell_price": sell_price,
        "divine_buy_price": divine_buy_price,
        "divine_sell_price": divine_sell_price,
        "dc_ratio": dc_ratio,  # 全域變數 dc_ratio
        "item_coin_value": item_coin_value,
        "profit_c_to_c": profit_c_to_c,
        "profit_c_to_d": profit_c_to_d,
        "purchasable_with_chaos": purchasable_with_chaos,
        "purchasable_with_divine": purchasable_with_divine
    }
    items.append(item_data)
    save_items_to_file()

    # 顯示在 Treeview 中
    display_item_in_treeview(tree, item_data)

    # 清除輸入欄位
    entry_item_name.delete(0, END)
    entry_receive_price.delete(0, END)
    entry_sell_price.delete(0, END)
    entry_divine_buy_price.delete(0, END)
    entry_divine_sell_price.delete(0, END)
    entry_item_coin_value.delete(0, END)

def delete_item():
    global tree, items
    selected = tree.selection()
    if not selected:
        messagebox.showerror("錯誤", "請選擇要刪除的紀錄。")
        return

    selected_item_id = selected[0]
    selected_index = tree.index(selected_item_id)
    
    # 從資料列表中刪除選中的項目
    del items[selected_index]

    # 從 TreeView 中刪除選中的項目
    tree.delete(selected_item_id)

    # 保存更新後的資料
    save_items_to_file()

    messagebox.showinfo("成功", "已成功刪除選中的紀錄。")


# 導出歷史紀錄為 CSV
def export_to_csv():
    global items
    export_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not export_file_path:
        return

    try:
        with open(export_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                "item_name", "receive_price", "sell_price", 
                "divine_buy_price", "divine_sell_price", 
                "profit_c_to_c", "profit_c_to_d", 
                "purchasable_with_chaos", "purchasable_with_divine"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in items:
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

# 主程式
def main():
    global tree, chaos_quantity_label, divine_quantity_label, root  # 使用全局變數
    global entry_item_name, entry_receive_price, entry_sell_price, entry_dc_ratio, entry_item_coin_value
    global entry_divine_buy_price, entry_divine_sell_price, dc_ratio_label

    root = tk.Tk()  # 初始化 root
    root.title("交易計算器")

    # 設置主框架
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 設置 Treeview
    columns = (
    "item_name", "receive_price", "sell_price", 
    "divine_buy_price", "divine_sell_price", 
    "profit_c_to_c", "profit_c_to_d", 
    "purchasable_with_chaos", "purchasable_with_divine"
)
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    tree.grid(row=7, column=0, columnspan=4, sticky='nsew')

    # 右上角DC比率
    dc_ratio_label = ttk.Label(main_frame, text=f"DC 比率: {dc_ratio}")
    dc_ratio_label.grid(row=0, column=2, padx=10, pady=2, sticky=tk.E)

    update_dc_button = ttk.Button(main_frame, text="修改 DC 比率", command=update_dc_ratio)
    update_dc_button.grid(row=0, column=3, padx=5, pady=2)

    # 倉庫混沌石數量和修改按鈕
    chaos_quantity_label = ttk.Label(main_frame, text=f"倉庫混沌石數量: {int(current_chaos // 1)}")
    chaos_quantity_label.grid(row=1, column=2, padx=10, pady=2, sticky=tk.E)

    chaos_button = ttk.Button(main_frame, text="修改混沌石數量", command=update_chaos_resources)
    chaos_button.grid(row=1, column=3, padx=5, pady=2)

    # 倉庫神聖石數量和修改按鈕
    divine_quantity_label = ttk.Label(main_frame, text=f"倉庫神聖石數量: {int(current_divine)}")
    divine_quantity_label.grid(row=2, column=2, padx=10, pady=2, sticky=tk.E)

    divine_button = ttk.Button(main_frame, text="修改神聖石數量", command=update_divine_resources)
    divine_button.grid(row=2, column=3, padx=5, pady=2)

    # 輸入欄位（保持原來的欄位位置）
    ttk.Label(main_frame, text="物品名稱:").grid(row=0, column=0, sticky=tk.W, pady=2)
    entry_item_name = ttk.Entry(main_frame, width=25)
    entry_item_name.grid(row=0, column=1, pady=2)

    ttk.Label(main_frame, text="混沌石購買價格:").grid(row=1, column=0, sticky=tk.W, pady=2)
    entry_receive_price = ttk.Entry(main_frame, width=25)
    entry_receive_price.grid(row=1, column=1, pady=2)

    ttk.Label(main_frame, text="混沌石販賣價格:").grid(row=2, column=0, sticky=tk.W, pady=2)
    entry_sell_price = ttk.Entry(main_frame, width=25)
    entry_sell_price.grid(row=2, column=1, pady=2)

    ttk.Label(main_frame, text="神聖石購買價格:").grid(row=3, column=0, sticky=tk.W, pady=2)
    entry_divine_buy_price = ttk.Entry(main_frame, width=25)
    entry_divine_buy_price.grid(row=3, column=1, pady=2)

    ttk.Label(main_frame, text="神聖石販賣價格:").grid(row=4, column=0, sticky=tk.W, pady=2)
    entry_divine_sell_price = ttk.Entry(main_frame, width=25)
    entry_divine_sell_price.grid(row=4, column=1, pady=2)

    ttk.Label(main_frame, text="單位物品價值 (金幣):").grid(row=5, column=0, sticky=tk.W, pady=2)
    entry_item_coin_value = ttk.Entry(main_frame, width=25)
    entry_item_coin_value.grid(row=5, column=1, pady=2)

    # 計算按鈕
    calculate_button = ttk.Button(main_frame, text="計算", command=calculate_profit)
    calculate_button.grid(row=6, column=0, columnspan=2, pady=10)

    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    tree.grid(row=7, column=0, columnspan=4, sticky='nsew')

    # 設置每個欄位的標題及對應列
    tree.heading("item_name", text="品項名字")
    tree.heading("receive_price", text="混沌石購買價格")
    tree.heading("sell_price", text="混沌石販賣價格")
    tree.heading("divine_buy_price", text="神聖石購買價格")
    tree.heading("divine_sell_price", text="神聖石販賣價格")
    tree.heading("profit_c_to_c", text="C買C賣利潤")
    tree.heading("profit_c_to_d", text="C買D賣利潤")
    tree.heading("purchasable_with_chaos", text="可用混沌石購買數量")
    tree.heading("purchasable_with_divine", text="可用神聖石購買數量")

    # 設置每個列的寬度
    tree.column("item_name", width=150)
    tree.column("receive_price", width=120, anchor=tk.CENTER)
    tree.column("sell_price", width=120, anchor=tk.CENTER)
    tree.column("divine_buy_price", width=120, anchor=tk.CENTER)
    tree.column("divine_sell_price", width=120, anchor=tk.CENTER)
    tree.column("profit_c_to_c", width=100, anchor=tk.CENTER)
    tree.column("profit_c_to_d", width=100, anchor=tk.CENTER)
    tree.column("purchasable_with_chaos", width=150, anchor=tk.CENTER)
    tree.column("purchasable_with_divine", width=150, anchor=tk.CENTER)
    
    # **在此處進行雙擊事件綁定**，這是初始化 Treeview 後的步驟
    tree.bind("<Double-1>", edit_single_column)

    # 刪除按鈕
    delete_button = ttk.Button(main_frame, text="刪除選中紀錄", command=delete_item)
    delete_button.grid(row=8, column=0, columnspan=2, pady=5)

    # 匯出 CSV 按鈕
    export_button = ttk.Button(main_frame, text="匯出為 CSV", command=export_to_csv)
    export_button.grid(row=9, column=0, columnspan=2, pady=5)

    # 讓 Treeview 填滿整個格子
    main_frame.rowconfigure(7, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # 加載歷史紀錄並顯示
    load_items_from_file()
    for item in items:
        display_item_in_treeview(tree, item)

    root.mainloop()

if __name__ == "__main__":
    main()
