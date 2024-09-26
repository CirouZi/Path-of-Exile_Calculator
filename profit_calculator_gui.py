import tkinter as tk
from tkinter import messagebox, ttk, END, simpledialog
import json
import os

# 文件名常量
DATA_FILE = "items_data.json"
items = []

# 加載保存的數據
def load_items_from_file():
    global items
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
        except json.JSONDecodeError:
            items = []
            print("歷史紀錄檔案內容有誤，將重新建立。")
        except Exception as e:
            items = []
            print(f"讀取歷史紀錄時發生錯誤: {e}")

# 保存數據
def save_items_to_file():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("錯誤", f"保存數據時發生錯誤: {e}")

# 將輸入中的分數轉換為小數
def parse_fraction(input_str):
    try:
        if '/' in input_str:
            numerator, denominator = input_str.split('/')
            return float(numerator) / float(denominator)
        else:
            return float(input_str)
    except ValueError:
        raise ValueError("請輸入有效的分數或數字。")

# 顯示選中物品的詳細信息
def show_item_details(selected_item_index):
    if selected_item_index is not None and 0 <= selected_item_index < len(items):
        selected_item = items[selected_item_index]
        details = (
            f"物品名稱: {selected_item['item_name']}\n"
            f"購買價格: {selected_item['receive_price']} chaos\n"
            f"販賣價格: {selected_item['sell_price']} chaos\n"
            f"DC比率: {selected_item['dc_ratio']}\n"
            f"單位物品價值: {selected_item['item_coin_value']} 金幣\n"
            f"1個D目前可買數量: {selected_item['bill1']}\n"
            f"1個D理論可收數量: {selected_item['bill2']}\n"
            f"利潤(C買C賣): {selected_item['profit_c_to_c']} C\n"
            f"利潤(C買D賣): {selected_item['profit_c_to_d']} C\n"
            f"賺取1C所需的金幣成本（C收C賣）: {selected_item['coin_cost_c_to_c']:.2f} 金幣\n"
            f"賺取1C所需的金幣成本（C買D賣，含D轉換C成本）: {selected_item['coin_cost_c_to_d']:.2f} 金幣\n"
            f"包含 D轉換C 所需金幣成本: {selected_item.get('d_to_c_coin_cost', 0.00):.2f} 金幣\n"
            f"可用混沌石購買的物品數量: {selected_item.get('purchasable_with_chaos', 0)}\n"
            f"可用神聖石購買的物品數量: {selected_item.get('purchasable_with_divine', 0)}\n"
        )
        messagebox.showinfo("歷史紀錄詳情", details)

# 顯示紀錄到 Treeview 並設置顏色
def display_item_in_treeview(tree, item_data):
    # 使用 .get() 方法來安全地獲取字典中的值，如果不存在則使用默認值 0.00
    profit_c_to_c = item_data.get('profit_c_to_c', 0.00)
    profit_c_to_d = item_data.get('profit_c_to_d', 0.00)
    coin_cost_c_to_c = item_data.get('coin_cost_c_to_c', 0.00)
    coin_cost_c_to_d = item_data.get('coin_cost_c_to_d', 0.00)
    d_to_c_coin_cost = item_data.get('d_to_c_coin_cost', 0.00)
    purchasable_with_chaos = item_data.get('purchasable_with_chaos', 0)
    purchasable_with_divine = item_data.get('purchasable_with_divine', 0)
    
    # 插入項目
    item_id = tree.insert("", END, values=(
        item_data['item_name'],
        f"{profit_c_to_c:.2f}",
        f"{profit_c_to_d:.2f}",
        f"{coin_cost_c_to_c:.2f}",
        f"{coin_cost_c_to_d:.2f}",
        purchasable_with_chaos,
        purchasable_with_divine
    ))
    
    # 設置顏色標籤，基於最大利潤設定顏色
    max_profit = max(profit_c_to_c, profit_c_to_d)
    if max_profit > 20:
        tree.item(item_id, tags=('high',))
    elif max_profit > 10:
        tree.item(item_id, tags=('medium',))
    else:
        tree.item(item_id, tags=('low',))

# 刪除選定的紀錄並更新 Treeview
def delete_item(selected_item_id, tree):
    global items
    if selected_item_id:
        try:
            # 獲取選定項目的索引
            selected_index = tree.index(selected_item_id)
            del items[selected_index]  # 刪除選定的紀錄
            save_items_to_file()  # 更新保存文件

            # 從 Treeview 中移除該項目
            tree.delete(selected_item_id)

            messagebox.showinfo("刪除成功", "紀錄已刪除。")
        except Exception as e:
            messagebox.showerror("錯誤", f"刪除紀錄時發生錯誤: {e}")
    else:
        messagebox.showerror("錯誤", "請選擇要刪除的紀錄。")

# 編輯購買數量函數
def edit_purchasable_quantities(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showerror("錯誤", "請選擇要編輯的紀錄。")
        return

    selected_item_id = selected[0]
    selected_index = tree.index(selected_item_id)
    selected_item = items[selected_index]

    # 獲取當前的購買數量
    current_purchasable_chaos = selected_item.get('purchasable_with_chaos', 0)
    current_purchasable_divine = selected_item.get('purchasable_with_divine', 0)

    # 彈出對話框讓用戶輸入新的購買數量
    new_purchasable_chaos = simpledialog.askinteger("編輯購買數量", 
                                                    "請輸入新的可用混沌石購買數量:",
                                                    initialvalue=current_purchasable_chaos, 
                                                    minvalue=0)
    if new_purchasable_chaos is None:
        return  # 用戶取消

    new_purchasable_divine = simpledialog.askinteger("編輯購買數量", 
                                                     "請輸入新的可用神聖石購買數量:",
                                                     initialvalue=current_purchasable_divine, 
                                                     minvalue=0)
    if new_purchasable_divine is None:
        return  # 用戶取消

    # 更新資料
    items[selected_index]['purchasable_with_chaos'] = new_purchasable_chaos
    items[selected_index]['purchasable_with_divine'] = new_purchasable_divine
    save_items_to_file()

    # 更新 Treeview
    tree.item(selected_item_id, values=(
        items[selected_index]['item_name'],
        f"{items[selected_index]['profit_c_to_c']:.2f}",
        f"{items[selected_index]['profit_c_to_d']:.2f}",
        f"{items[selected_index]['coin_cost_c_to_c']:.2f}",
        f"{items[selected_index]['coin_cost_c_to_d']:.2f}",
        items[selected_index]['purchasable_with_chaos'],
        items[selected_index]['purchasable_with_divine']
    ))

    messagebox.showinfo("更新成功", "購買數量已更新。")

# 利潤計算函數
def calculate_profit(tree):
    try:
        item_name = entry_item_name.get().strip()
        if not item_name:
            raise ValueError("物品名稱不能為空。")
        
        receive_price = float(entry_receive_price.get())  # 購買價格 (chaos)
        sell_price = float(entry_sell_price.get())  # 販賣價格 (chaos)
        dc_ratio = float(entry_dc_ratio.get())  # DC 比率 (D換C的比值)
        item_coin_value = float(entry_item_coin_value.get())  # 單位物品價值 (金幣)

        # 將 1個D目前可買數量 和 1個D理論可收數量處理為小數
        bill1_input = entry_bill1.get().strip()
        bill2_input = entry_bill2.get().strip()
        bill1 = parse_fraction(bill1_input)  # 1個D目前可以買到的數量 物品:D
        bill2 = parse_fraction(bill2_input)  # 1個D理論可以收到的數量 D:物品

        # 新增：現有混沌石和神聖石數量
        current_chaos_input = entry_current_chaos.get().strip()
        current_divine_input = entry_current_divine.get().strip()
        current_chaos = float(current_chaos_input) if current_chaos_input else 0.0  # 現有混沌石數量
        current_divine = float(current_divine_input) if current_divine_input else 0.0  # 現有神聖石數量

        # 計算換D賣的等價價值
        sell_div_num_chaos = (1 / bill1) * dc_ratio if bill1 != 0 else 0

        # 計算各項費用和收益
        receive_chaos = receive_price  # 收裝備用的C (chaos)
        receive_coin = item_coin_value  # 收東西花費的金幣
        sell_chaos = sell_price  # 賣東西的C (chaos)
        sell_coin = sell_price * 25  # 賣東西花費的金幣
        extra_coin = sell_div_num_chaos * 25  # 換D時額外消耗的金幣

        # 計算D換C的金幣成本
        d_to_c_coin_cost = dc_ratio * 25  # D換C的金幣成本

        # 計算C收C賣的利潤
        prof_c_to_c = sell_chaos - receive_chaos

        # 計算C買D賣的利潤
        prof_c_to_d = sell_div_num_chaos - receive_chaos

        # 計算賺取1C所需的金幣成本（C收C賣）
        if prof_c_to_c != 0:
            coin_cost_c_to_c = (receive_coin + sell_coin) / prof_c_to_c
        else:
            coin_cost_c_to_c = 0

        # 計算賺取1C所需的金幣成本（C買D賣，含D換C成本）
        if prof_c_to_d != 0:
            total_coin_cost_c_to_d = receive_coin + extra_coin + d_to_c_coin_cost  # 包括D換C的成本
            coin_cost_c_to_d = total_coin_cost_c_to_d / prof_c_to_d
        else:
            coin_cost_c_to_d = 0

        # 計算可購買的物品數量
        purchasable_with_chaos = int(current_chaos // receive_price) if receive_price > 0 else 0
        purchasable_with_divine = int((current_divine * dc_ratio) // receive_price) if receive_price > 0 else 0
        total_purchasable = purchasable_with_chaos + purchasable_with_divine

        # 顯示結果
        result = (
            f"物品名稱: {item_name}\n"
            f"購買價格: {receive_price} chaos\n"
            f"販賣價格: {sell_price} chaos\n"
            f"1個D目前可以直接買到{bill1:.2f}個該物品，理論D賣價格: {sell_div_num_chaos:.2f} C\n"
            f"當前DC比率: {dc_ratio}\n"
            f"單位物品價值: {item_coin_value} 金幣\n"
            f"現有混沌石數量: {current_chaos}\n"
            f"現有神聖石數量: {current_divine}\n"
            "--------------------------------\n"
            f"C收C賣，利潤是: {prof_c_to_c} C\n"
            f"C買D賣，利潤是: {prof_c_to_d} C\n"
            f"賺取1C所需的金幣成本（C收C賣）: {coin_cost_c_to_c:.2f} 金幣\n"
            f"賺取1C所需的金幣成本（C買D賣，含D轉換C成本）: {coin_cost_c_to_d:.2f} 金幣\n"
            f"包含 D轉換C 所需金幣成本: {d_to_c_coin_cost:.2f} 金幣\n"
            "--------------------------------\n"
            f"可用混沌石購買的物品數量: {purchasable_with_chaos}\n"
            f"可用神聖石購買的物品數量: {purchasable_with_divine}\n"
            f"總可購買的物品數量: {total_purchasable}\n"
        )
        result += "--------------------------------\n"
        messagebox.showinfo("結果", result)

        # 保存計算結果到歷史紀錄
        item_data = {
            "item_name": item_name,
            "receive_price": receive_price,
            "sell_price": sell_price,
            "dc_ratio": dc_ratio,
            "item_coin_value": item_coin_value,
            "bill1": bill1,
            "bill2": bill2,
            "profit_c_to_c": prof_c_to_c,
            "profit_c_to_d": prof_c_to_d,
            "coin_cost_c_to_c": coin_cost_c_to_c,
            "coin_cost_c_to_d": coin_cost_c_to_d,
            "d_to_c_coin_cost": d_to_c_coin_cost,
            "current_chaos": current_chaos,
            "current_divine": current_divine,
            "purchasable_with_chaos": purchasable_with_chaos,
            "purchasable_with_divine": purchasable_with_divine,
            "total_purchasable": total_purchasable,
        }

        # 保存紀錄並更新 Treeview
        items.append(item_data)
        save_items_to_file()

        # 更新 Treeview 並根據利潤變更顏色
        display_item_in_treeview(tree, item_data)

    except ValueError as ve:
        messagebox.showerror("錯誤", str(ve))
    except Exception as e:
        messagebox.showerror("錯誤", f"計算時發生未知錯誤: {e}")

# 主函數
def main():
    root = tk.Tk()
    root.title("交易計算器")

    # 設置主框架
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 輸入欄位
    ttk.Label(main_frame, text="物品名稱:").grid(row=0, column=0, sticky=tk.W, pady=2)
    global entry_item_name
    entry_item_name = ttk.Entry(main_frame, width=25)
    entry_item_name.grid(row=0, column=1, pady=2)

    ttk.Label(main_frame, text="購買價格 (chaos):").grid(row=1, column=0, sticky=tk.W, pady=2)
    global entry_receive_price
    entry_receive_price = ttk.Entry(main_frame, width=25)
    entry_receive_price.grid(row=1, column=1, pady=2)

    ttk.Label(main_frame, text="販賣價格 (chaos):").grid(row=2, column=0, sticky=tk.W, pady=2)
    global entry_sell_price
    entry_sell_price = ttk.Entry(main_frame, width=25)
    entry_sell_price.grid(row=2, column=1, pady=2)

    ttk.Label(main_frame, text="DC 比率:").grid(row=3, column=0, sticky=tk.W, pady=2)
    global entry_dc_ratio
    entry_dc_ratio = ttk.Entry(main_frame, width=25)
    entry_dc_ratio.grid(row=3, column=1, pady=2)

    ttk.Label(main_frame, text="單位物品價值 (金幣):").grid(row=4, column=0, sticky=tk.W, pady=2)
    global entry_item_coin_value
    entry_item_coin_value = ttk.Entry(main_frame, width=25)
    entry_item_coin_value.grid(row=4, column=1, pady=2)

    ttk.Label(main_frame, text="1個D目前可買數量:").grid(row=5, column=0, sticky=tk.W, pady=2)
    global entry_bill1
    entry_bill1 = ttk.Entry(main_frame, width=25)
    entry_bill1.grid(row=5, column=1, pady=2)

    ttk.Label(main_frame, text="1個D理論可收數量:").grid(row=6, column=0, sticky=tk.W, pady=2)
    global entry_bill2
    entry_bill2 = ttk.Entry(main_frame, width=25)
    entry_bill2.grid(row=6, column=1, pady=2)

    # 新增輸入欄位：現有混沌石和神聖石數量
    ttk.Label(main_frame, text="現有混沌石數量:").grid(row=7, column=0, sticky=tk.W, pady=2)
    global entry_current_chaos
    entry_current_chaos = ttk.Entry(main_frame, width=25)
    entry_current_chaos.grid(row=7, column=1, pady=2)

    ttk.Label(main_frame, text="現有神聖石數量:").grid(row=8, column=0, sticky=tk.W, pady=2)
    global entry_current_divine
    entry_current_divine = ttk.Entry(main_frame, width=25)
    entry_current_divine.grid(row=8, column=1, pady=2)

    # 計算按鈕
    calculate_button = ttk.Button(main_frame, text="計算", command=lambda: calculate_profit(tree))
    calculate_button.grid(row=9, column=0, columnspan=2, pady=10)

    # 歷史紀錄欄位設置
    columns = ("item_name", "profit_c_to_c", "profit_c_to_d", "coin_cost_c_to_c", "coin_cost_c_to_d", "purchasable_with_chaos", "purchasable_with_divine")
    tree = ttk.Treeview(main_frame, columns=columns, show='headings', selectmode='browse')
    tree.grid(row=0, column=2, rowspan=12, padx=10, pady=2)

    # 定義欄位
    tree.heading("item_name", text="品項名字")
    tree.heading("profit_c_to_c", text="C買C賣利潤 (C)")
    tree.heading("profit_c_to_d", text="C買D賣利潤 (C)")
    tree.heading("coin_cost_c_to_c", text="賺取1C所需的金幣成本 (C收C賣)")
    tree.heading("coin_cost_c_to_d", text="賺取1C所需的金幣成本 (C買D賣)")
    tree.heading("purchasable_with_chaos", text="可用混沌石購買數量")
    tree.heading("purchasable_with_divine", text="可用神聖石購買數量")

    # 設置欄位寬度
    tree.column("item_name", width=150)
    tree.column("profit_c_to_c", width=120, anchor=tk.CENTER)
    tree.column("profit_c_to_d", width=120, anchor=tk.CENTER)
    tree.column("coin_cost_c_to_c", width=200, anchor=tk.CENTER)
    tree.column("coin_cost_c_to_d", width=200, anchor=tk.CENTER)
    tree.column("purchasable_with_chaos", width=150, anchor=tk.CENTER)
    tree.column("purchasable_with_divine", width=150, anchor=tk.CENTER)

    # 定義標籤樣式
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)

    # 定義顏色標籤
    tree.tag_configure('high', foreground='red')
    tree.tag_configure('medium', foreground='green')
    tree.tag_configure('low', foreground='black')

    # 刪除按鈕
    delete_button = ttk.Button(main_frame, text="刪除選中紀錄", state="disabled",
                               command=lambda: delete_item(tree.selection()[0] if tree.selection() else None, tree))
    delete_button.grid(row=10, column=2, pady=10)

    # 編輯購買數量按鈕
    edit_button = ttk.Button(main_frame, text="編輯購買數量", state="disabled",
                             command=lambda: edit_purchasable_quantities(tree))
    edit_button.grid(row=11, column=2, pady=5)

    # 綁定雙擊事件來顯示詳細信息
    tree.bind("<Double-1>", lambda event: show_item_details(tree.index(tree.selection()[0]) if tree.selection() else None))

    # 綁定選擇事件來啟用刪除和編輯按鈕
    def on_tree_select(event):
        selected = tree.selection()
        if selected:
            delete_button.config(state="normal")
            edit_button.config(state="normal")
        else:
            delete_button.config(state="disabled")
            edit_button.config(state="disabled")

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # 綁定點擊空白處的事件來取消選擇
    def on_click_blank(event):
        region = tree.identify_region(event.x, event.y)
        if region == "nothing":  # 點擊的是空白處
            tree.selection_remove(tree.selection())  # 取消選擇
            delete_button.config(state="disabled")
            edit_button.config(state="disabled")

    # 綁定左鍵點擊空白處的事件
    tree.bind("<Button-1>", on_click_blank)

    # 加載歷史紀錄並顯示
    load_items_from_file()
    for item in items:
        display_item_in_treeview(tree, item)

    root.mainloop()

if __name__ == "__main__":
    main()
