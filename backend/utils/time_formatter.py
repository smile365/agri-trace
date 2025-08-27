#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间格式化工具类
支持将微秒时间戳转换为各种日期格式
"""

import datetime
from typing import Optional, Union


class TimeFormatter:
    """
    时间格式化工具类
    支持将微秒时间戳转换为指定的日期格式
    """
    
    
    @classmethod
    def format_timestamp(cls, timestamp_ms: Union[int, float, str], 
                        date_formatter: str = 'yyyy-MM-dd HH:mm:ss') -> Optional[str]:
        """
        将毫秒时间戳格式化为指定格式的日期字符串
        Args:
            timestamp_ms: 毫秒秒时间戳（可以是int、float或str类型）
            date_formatter: 日期格式（如：yyyy/MM/dd HH:mm、yyyy-MM-dd等）
        Returns:
            格式化后的日期字符串，如果转换失败返回None
        """
        try:
            # 转换为float类型的时间戳
            if isinstance(timestamp_ms, str):
                timestamp_ms = float(timestamp_ms)
            # 将毫秒时间戳转换为秒（保留小数部分以维持毫秒精度）
            timestamp_sec = timestamp_ms / 1000.0
            dt = datetime.datetime.fromtimestamp(timestamp_sec)
            # 将格式字符串中的关键字替换为datetime支持的格式符
            format_mapping = {
                'yyyy': '%Y',
                'MM': '%m',
                'dd': '%d',
                'HH': '%H',
                'mm': '%M',
                'ss': '%S'
            }
            
            for key, value in format_mapping.items():
                date_formatter = date_formatter.replace(key, value)
            
            return dt.strftime(date_formatter)
                    
        except (ValueError, TypeError, OSError) as e:
            print(f"时间格式化错误: {e}")
            return timestamp_ms
    
    @classmethod
    def format_current_time(cls, date_formatter: str = 'yyyy-MM-dd HH:mm:ss') -> str:
        """
        格式化当前时间
        
        Args:
            date_formatter: 日期格式
            
        Returns:
            格式化后的当前时间字符串
        """
        current_timestamp = datetime.datetime.now().timestamp() * 1000000
        return cls.format_timestamp(current_timestamp, date_formatter)
    
    @classmethod
    def _convert_format(cls, date_formatter: str) -> str:
        """
        将自定义格式转换为Python strftime格式
        
        Args:
            date_formatter: 自定义日期格式
            
        Returns:
            Python strftime格式字符串
        """
        # 如果是预定义格式，直接返回
        if date_formatter in cls.FORMAT_MAPPING:
            return cls.FORMAT_MAPPING[date_formatter]
        
        # 使用更精确的替换方式，避免冲突
        import re
        
        python_format = date_formatter
        
        # 使用正则表达式进行精确替换，避免部分匹配问题
        replacements = [
            (r'yyyy', '%Y'),  # 四位年份
            (r'yy', '%y'),    # 两位年份
            (r'MM', '%m'),    # 两位月份
            (r'dd', '%d'),    # 两位日期
            (r'HH', '%H'),    # 24小时制小时
            (r'mm', '%M'),    # 分钟
            (r'ss', '%S'),    # 秒
        ]
        
        # 按顺序进行替换
        for pattern, replacement in replacements:
            python_format = re.sub(pattern, replacement, python_format)
        
        # 处理单字符格式（在双字符格式处理完成后）
        single_replacements = [
            (r'(?<!%)M(?!M)', '%m'),  # 单个M（月份），但不匹配%M或MM
            (r'(?<!%)d(?!d)', '%d'),  # 单个d（日期），但不匹配%d或dd
            (r'(?<!%)H(?!H)', '%H'),  # 单个H（小时），但不匹配%H或HH
        ]
        
        for pattern, replacement in single_replacements:
            python_format = re.sub(pattern, replacement, python_format)
        
        return python_format
    
    @classmethod
    def get_supported_formats(cls) -> list:
        """
        获取支持的预定义格式列表
        
        Returns:
            支持的格式列表
        """
        return list(cls.FORMAT_MAPPING.keys())
    
    @classmethod
    def validate_timestamp(cls, timestamp: Union[int, float, str]) -> bool:
        """
        验证时间戳是否有效
        
        Args:
            timestamp: 要验证的时间戳
            
        Returns:
            True如果时间戳有效，False否则
        """
        try:
            if isinstance(timestamp, str):
                timestamp = float(timestamp)
            elif isinstance(timestamp, int):
                timestamp = float(timestamp)
            
            # 微秒时间戳转换为秒时间戳
            timestamp_seconds = timestamp / 1000000
            
            # 检查时间戳范围（1970-2100年之间）
            if timestamp_seconds < 0 or timestamp_seconds > 4102444800:  # 2100-01-01
                return False
            
            # 尝试创建datetime对象
            datetime.datetime.fromtimestamp(timestamp_seconds)
            return True
            
        except (ValueError, TypeError, OSError):
            return False


# 便捷函数
def format_microsecond_timestamp(timestamp: Union[int, float, str], 
                                date_formatter: str = 'yyyy-MM-dd HH:mm:ss') -> Optional[str]:
    """
    格式化微秒时间戳的便捷函数
    
    Args:
        timestamp: 微秒时间戳
        date_formatter: 日期格式
        
    Returns:
        格式化后的日期字符串
    """
    return TimeFormatter.format_timestamp(timestamp, date_formatter)


def get_current_formatted_time(date_formatter: str = 'yyyy-MM-dd HH:mm:ss') -> str:
    """
    获取当前格式化时间的便捷函数
    
    Args:
        date_formatter: 日期格式
        
    Returns:
        格式化后的当前时间字符串
    """
    return TimeFormatter.format_current_time(date_formatter)


if __name__ == '__main__':
    # 测试代码
    print("时间格式化工具测试:")
    created_time = 1755525976000
    created_time_formatted = "2025-08-18 22:06:16"
    print(format_microsecond_timestamp(created_time, 'yyyy-MM-dd HH:mm:ss')==created_time_formatted)