import win32gui
import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

# 指定 Tesseract 的路徑
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 根據您的系統調整此路徑

# 獲取 Path of Exile 視窗句柄
poe_window = gw.getWindowsWithTitle('Path of Exile')[0]
hwnd = poe_window._hWnd

# 將視窗移到最前方
win32gui.ShowWindow(hwnd, 5)  # 5 表示正常顯示
win32gui.SetForegroundWindow(hwnd)

# 等待一段時間以確保視窗處於前景
time.sleep(1)

# 獲取視窗的位置和大小
rect = poe_window.left, poe_window.top, poe_window.width, poe_window.height
print(f"視窗位置和大小: {rect}")

# 定義螢幕和遊戲的解析度
screen_resolution = (1920, 1080)  # 螢幕解析度
game_resolution = (1600, 900)     # Path of Exile 視窗解析度

# 計算縮放比例
scale_x = game_resolution[0] / screen_resolution[0]  # 水平縮放比例
scale_y = game_resolution[1] / screen_resolution[1]  # 垂直縮放比例

# 混沌石與神聖石的遊戲內相對座標 (經過調整的座標)
chaos_game_pos = (530, 280)  # 混沌石 + 數字
divine_game_pos = (580, 340)  # 神聖石 + 數字

# 計算螢幕上的實際座標
chaos_x = rect[0] + int(chaos_game_pos[0] * scale_x)
chaos_y = rect[1] + int(chaos_game_pos[1] * scale_y)
divine_x = rect[0] + int(divine_game_pos[0] * scale_x)
divine_y = rect[1] + int(divine_game_pos[1] * scale_y)

# 調整擷取範圍
chaos_width = int(60 * scale_x)  # 根據縮放比例調整寬度
chaos_height = int(50 * scale_y)  # 根據縮放比例調整高度
divine_width = int(60 * scale_x)  # 根據縮放比例調整寬度
divine_height = int(50 * scale_y)  # 根據縮放比例調整高度

# 設置擷取區域
chaos_region = (chaos_x, chaos_y, chaos_width, chaos_height)  # 混沌石擷取區域
divine_region = (divine_x, divine_y, divine_width, divine_height)  # 神聖石擷取區域

# 使用 pyautogui 擷取
chaos_screenshot = pyautogui.screenshot(region=chaos_region)
divine_screenshot = pyautogui.screenshot(region=divine_region)

# 圖片輕度預處理，主要增強對比度並去除部分噪聲
def minimal_preprocess_image(image):
    # 轉換為灰度圖像
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # 輕微增強對比度
    contrast_image = cv2.convertScaleAbs(gray_image, alpha=1.5, beta=20)
    
    # 高斯模糊去噪
    blurred_image = cv2.GaussianBlur(contrast_image, (3, 3), 0)
    
    return blurred_image

# 使用 Tesseract 提取數字
def extract_text_from_image(image, psm_mode="7"):
    config = f"--psm {psm_mode} digits"
    text = pytesseract.image_to_string(image, config=config)
    return ''.join(filter(str.isdigit, text))  # 僅保留數字

# 輕度預處理混沌石和神聖石圖片
chaos_processed = minimal_preprocess_image(chaos_screenshot)
divine_processed = minimal_preprocess_image(divine_screenshot)

# 保存處理後的圖片以便進一步分析
cv2.imwrite('chaos_minimal_processed.png', chaos_processed)
cv2.imwrite('divine_minimal_processed.png', divine_processed)

# 從處理後的圖片中提取數字
chaos_quantity = extract_text_from_image(chaos_processed, psm_mode="6")
divine_quantity = extract_text_from_image(divine_processed, psm_mode="7")

# 打印識別結果
print(f"混沌石數量: {chaos_quantity}")
print(f"神聖石數量: {divine_quantity}")