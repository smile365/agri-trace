"""
DHT11传感器数据处理工具
"""
import base64
import json
import logging

logger = logging.getLogger(__name__)

def decode_baidu_lot_message(data):
    """
    解码 百度智能云 lot 透传数据
    """
    # 1. 提取并解码 message 字段
    encoded_str = data["message"]
    #print(f"原始数据: {encoded_str}")
    decoded_bytes = base64.b64decode(encoded_str)  # 解码为字节流
    # 2. 转换为 UTF-8 字符串（原始数据）
    original_data = decoded_bytes.decode("utf-8")  # 
    #print(f"原始数据: {original_data}")
    return original_data

def decode_nt1b_message(data):
    """
    解码 NT1B 传感器数据
    """
    original_str = decode_baidu_lot_message(data)  # 得到 "53.0 26.9"
    original_data = json.loads(original_str)
    return original_data

def decode_dht11_message(data):
    """
    解码DHT11传感器数据
    
    Args:
        data (dict): 接收到的原始JSON数据，包含base64编码的message字段
        
    Returns:
        dict: 解码后的温湿度数据，格式为 {"humidity": "53.0", "temperature": "26.9"}
        
    Raises:
        ValueError: 当数据格式不正确时抛出异常
        KeyError: 当缺少必要字段时抛出异常
    """
    original_data = decode_baidu_lot_message(data)  # 得到 "53.0 26.9"
    print(f"原始数据: {original_data}")
    # 3. 分割为温湿度值
    humidity, temperature = original_data.split(" ")
    return_data = {"humidity":humidity,"temperature":temperature}
    #print(f"湿度: {humidity}%, 温度: {temperature}°C")
    return return_data