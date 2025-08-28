"""
DHT11传感器数据处理工具
"""
import base64
import json
import logging

logger = logging.getLogger(__name__)

def decode_b64(encoded_str:str)->str:
    """
    解码 base64 数据
    """
    decoded_bytes = base64.b64decode(encoded_str)  # 解码为字节流
    # 2. 转换为 UTF-8 字符串（原始数据）
    original_data = decoded_bytes.decode("utf-8")  # 
    #print(f"原始数据: {original_data}")
    return original_data

def decode_bdlot_data(data:dict)->dict:
    """
    解码 百度智能云 lot 透传数据
    """
    original_str = decode_b64(data["message"])
    try:
        original_data = json.loads(original_str)
        data["message"] = original_data
    except json.JSONDecodeError:
        data["message"] = original_str
    return data

def decode_bdlot_msg(data:dict):
    """
    解码 百度智能云 lot 透传数据
    """
    original_str = decode_b64(data["message"])
    try:
        return json.loads(original_str)
    except json.JSONDecodeError as e:
        #logger.info(f"原始数据: {original_str}")
        #logger.error(f"错误信息: {e}")
        return original_str


def temperature_humidity2json(original_data:str)->dict:
    humidity, temperature = original_data.split(" ")
    return_data = {"humidity":humidity,"temperature":temperature}
    #print(f"湿度: {humidity}%, 温度: {temperature}°C")
    return return_data