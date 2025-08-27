#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间格式化工具使用示例
演示如何在项目中使用TimeFormatter类
"""

from time_formatter import TimeFormatter, format_microsecond_timestamp, get_current_formatted_time


def demo_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 示例微秒时间戳（飞书API返回的时间戳格式）
    feishu_timestamp = 1640995200000000  # 2022-01-01 08:00:00
    
    # 使用类方法格式化
    formatted_time = TimeFormatter.format_timestamp(feishu_timestamp, 'yyyy-MM-dd HH:mm')
    print(f"飞书时间戳 {feishu_timestamp} 格式化为: {formatted_time}")
    
    # 使用便捷函数格式化
    formatted_time2 = format_microsecond_timestamp(feishu_timestamp, 'yyyy/MM/dd')
    print(f"使用便捷函数格式化: {formatted_time2}")
    
    # 获取当前时间
    current_time = get_current_formatted_time('yyyy年MM月dd日 HH:mm:ss')
    print(f"当前时间: {current_time}")


def demo_different_formats():
    """不同格式示例"""
    print("\n=== 不同格式示例 ===")
    
    timestamp = 1640995200000000
    
    formats = [
        ('yyyy-MM-dd HH:mm:ss', '标准日期时间'),
        ('yyyy/MM/dd HH:mm', '斜杠分隔日期时间'),
        ('yyyy-MM-dd', '仅日期'),
        ('HH:mm:ss', '仅时间'),
        ('yyyy年MM月dd日', '中文日期'),
        ('MM/dd/yyyy', '美式日期'),
        ('dd/MM/yyyy', '欧式日期'),
    ]
    
    for fmt, desc in formats:
        result = TimeFormatter.format_timestamp(timestamp, fmt)
        print(f"{desc:12} ({fmt:20}): {result}")


def demo_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    # 测试无效时间戳
    invalid_timestamps = [
        'invalid_string',
        -1,
        None,
        '',
        9999999999999999999  # 超出范围的时间戳
    ]
    
    for invalid_ts in invalid_timestamps:
        result = TimeFormatter.format_timestamp(invalid_ts, 'yyyy-MM-dd')
        is_valid = TimeFormatter.validate_timestamp(invalid_ts) if invalid_ts is not None else False
        print(f"时间戳 {invalid_ts} -> 格式化结果: {result}, 有效性: {is_valid}")


def demo_feishu_integration():
    """飞书集成示例"""
    print("\n=== 飞书集成示例 ===")
    
    # 模拟飞书API返回的数据
    feishu_data = {
        'created_time': '1640995200000000',  # 字符串格式的微秒时间戳
        'updated_time': 1641081600000000,    # 数字格式的微秒时间戳
    }
    
    # 模拟不同的date_formatter配置（来自飞书字段配置）
    date_formatters = {
        'created_time': 'yyyy-MM-dd HH:mm',
        'updated_time': 'yyyy/MM/dd',
    }
    
    print("飞书数据时间字段格式化:")
    for field, timestamp in feishu_data.items():
        formatter = date_formatters.get(field, 'yyyy-MM-dd HH:mm:ss')
        formatted = TimeFormatter.format_timestamp(timestamp, formatter)
        print(f"{field}: {timestamp} -> {formatted} (格式: {formatter})")


def demo_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 模拟批量时间戳数据
    timestamps = [
        1640995200000000,  # 2022-01-01 08:00:00
        1641081600000000,  # 2022-01-02 08:00:00
        1641168000000000,  # 2022-01-03 08:00:00
    ]
    
    formatter = 'yyyy-MM-dd'
    
    print(f"批量格式化 {len(timestamps)} 个时间戳:")
    formatted_times = []
    for i, ts in enumerate(timestamps, 1):
        formatted = TimeFormatter.format_timestamp(ts, formatter)
        formatted_times.append(formatted)
        print(f"{i}. {ts} -> {formatted}")
    
    print(f"\n格式化结果列表: {formatted_times}")


if __name__ == '__main__':
    # 运行所有示例
    demo_basic_usage()
    demo_different_formats()
    demo_error_handling()
    demo_feishu_integration()
    demo_batch_processing()
    
    print("\n=== 支持的预定义格式 ===")
    supported_formats = TimeFormatter.get_supported_formats()
    for i, fmt in enumerate(supported_formats, 1):
        print(f"{i:2}. {fmt}")