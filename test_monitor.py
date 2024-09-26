import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import tkinter as tk
from item_manager_app import ItemManagerApp  # 假設已保存為 item_manager_app.py

class TestItemManagerApp(unittest.TestCase):

    def setUp(self):
        """設置測試的初始環境"""
        self.root = tk.Tk()
        self.app = ItemManagerApp(self.root)

    def tearDown(self):
        """在每次測試後清理 Tkinter"""
        self.root.destroy()

    @patch("builtins.open", new_callable=mock_open, read_data='{"items": [], "current_chaos": 100.0, "current_divine": 5.0, "dc_ratio": 1.2}')
    def test_load_items_from_file(self, mock_file):
        """測試從文件加載物品"""
        self.app.load_items_from_file()
        self.assertEqual(self.app.current_chaos, 100.0)
        self.assertEqual(self.app.current_divine, 5.0)
        self.assertEqual(self.app.dc_ratio, 1.2)
        mock_file.assert_called_once_with(self.app.DATA_FILE, "r", encoding="utf-8")

@patch("builtins.open", new_callable=mock_open)
def test_save_items_to_file(self, mock_file):
    """測試保存物品到文件"""
    self.app.items = [{"item_name": "Item1", "receive_price": 10.0}]
    self.app.current_chaos = 100.0
    self.app.current_divine = 100.0
    self.app.dc_ratio = 150.0

    self.app.save_items_to_file()

    # 構造預期寫入的 JSON 字符串
    expected_data = json.dumps({
        "items": self.app.items,
        "current_chaos": self.app.current_chaos,
        "current_divine": self.app.current_divine,
        "dc_ratio": self.app.dc_ratio
    }, ensure_ascii=False, indent=4)

    # 將 mock_file 所有 write 調用的內容串接在一起進行比較
    handle = mock_file()
    written_data = ''.join(call[0][0] for call in handle.write.call_args_list)

    self.assertEqual(written_data, expected_data)


    def test_calculate_profit(self):
        """測試計算利潤"""
        self.app.dc_ratio = 1.0  # 確保使用默認的 dc_ratio

        # 設置輸入欄位的值
        self.app.entry_item_name.insert(0, "Item1")
        self.app.entry_receive_price.insert(0, "10")
        self.app.entry_sell_price.insert(0, "20")
        self.app.entry_divine_buy_price.insert(0, "5")
        self.app.entry_divine_sell_price.insert(0, "25")
        self.app.entry_item_coin_value.insert(0, "50")

        # 執行計算
        self.app.calculate_profit()

        # 檢查物品是否正確計算
        self.assertEqual(len(self.app.items), 1)
        item = self.app.items[0]
        self.assertEqual(item['profit_c_to_c'], 10.0)  # 20 - 10
        self.assertEqual(item['profit_c_to_d'], 20.0)  # (25 * dc_ratio) - 10

    @patch("tkinter.messagebox.showerror")
    def test_calculate_profit_invalid_input(self, mock_showerror):
        """測試輸入錯誤時的行為"""
        self.app.entry_item_name.insert(0, "Item1")
        self.app.entry_receive_price.insert(0, "invalid")  # 無效的輸入
        self.app.calculate_profit()

        mock_showerror.assert_called_once_with("錯誤", "請輸入有效的數字。")

    def test_delete_item(self):
        """測試刪除物品"""
        # 添加一個物品
        self.app.items = [{"item_name": "Item1", "receive_price": 10.0}]
        self.app.display_item_in_treeview(self.app.items[0])

        # 模擬選中第一行
        self.app.tree.selection = MagicMock(return_value=(self.app.tree.get_children()[0],))

        # 刪除選中的物品
        self.app.delete_item()

        # 確認物品已刪除
        self.assertEqual(len(self.app.items), 0)

    @patch("tkinter.filedialog.asksaveasfilename", return_value="test.csv")
    @patch("builtins.open", new_callable=mock_open)
    def test_export_to_csv(self, mock_open_file, mock_dialog):
        """測試匯出 CSV"""
        self.app.items = [{"item_name": "Item1", "receive_price": 10.0}]
        self.app.export_to_csv()
        mock_open_file.assert_called_once_with("test.csv", 'w', newline='', encoding='utf-8-sig')

if __name__ == "__main__":
    unittest.main(exit=False)
