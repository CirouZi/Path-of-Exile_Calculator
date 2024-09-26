def parse_fractional_input(value_str):
    """解析分數或浮點數輸入"""
    try:
        if '/' in value_str:
            numerator, denominator = value_str.split('/')
            return float(numerator) / float(denominator)
        else:
            return float(value_str)
    except ValueError:
        raise ValueError("無效的輸入格式")

def calculate_profit_logic(receive_price, sell_price, divine_sell_price, dc_ratio):
    """計算 C買C賣 和 C買D賣 利潤"""
    profit_c_to_c = sell_price - receive_price
    profit_c_to_d = (divine_sell_price * dc_ratio) - receive_price
    return profit_c_to_c, profit_c_to_d
