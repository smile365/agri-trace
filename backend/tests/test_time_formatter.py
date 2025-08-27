#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间格式化工具测试
测试 TimeFormatter 类的各种功能
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.time_formatter import (
    TimeFormatter, 
    format_microsecond_timestamp, 
    get_current_formatted_time
)


class TestTimeFormatter(unittest.TestCase):
    """时间格式化工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 测试用的微秒时间戳（对应 2025-08-18 22:06:16）
        self.test_timestamp = 1755525976000
        self.expected_formatted = "2025-08-18 22:06:16"
        
        # 其他测试时间戳
        self.timestamp_2022 = 1640995200000000  # 2022-01-01 08:00:00
        self.timestamp_str = "1640995200000000"  # 字符串格式
    
    def test_specific_timestamp_formatting(self):
        """测试特定时间戳格式化（对应 time_formatter.py L212-214）"""
        # 测试第212行的时间戳
        created_time = 1755525976000
        
        # 注意：这个时间戳看起来是毫秒级别，不是微秒级别
        # 需要转换为微秒级别进行测试
        created_time_microseconds = created_time * 1000
        
        # 测试格式化结果
        result = format_microsecond_timestamp(created_time_microseconds, 'yyyy-MM-dd HH:mm:ss')
        
        # 验证结果不为None
        self.assertIsNotNone(result)
        
        # 验证格式正确（年份应该是合理的）
        self.assertTrue(result.startswith('20'))  # 应该是21世纪的年份
        
        print(f"原始时间戳: {created_time}")
        print(f"微秒时间戳: {created_time_microseconds}")
        print(f"格式化结果: {result}")
    
    def test_format_timestamp_basic(self):
        """测试基本时间戳格式化"""
        result = TimeFormatter.format_timestamp(self.timestamp_2022, 'yyyy-MM-dd HH:mm:ss')
        self.assertEqual(result, '2022-01-01 08:00:00')
    
    def test_format_timestamp_different_formats(self):
        """测试不同格式的时间戳格式化"""
        test_cases = [
            ('yyyy-MM-dd', '2022-01-01'),
            ('yyyy/MM/dd', '2022/01/01'),
            ('yyyy年MM月dd日', '2022年01月01日'),
            ('HH:mm:ss', '08:00:00'),
            ('MM/dd/yyyy', '01/01/2022'),
        ]
        
        for format_str, expected in test_cases:
            with self.subTest(format=format_str):
                result = TimeFormatter.format_timestamp(self.timestamp_2022, format_str)
                self.assertEqual(result, expected)
    
    def test_format_timestamp_string_input(self):
        """测试字符串类型的时间戳输入"""
        result = TimeFormatter.format_timestamp(self.timestamp_str, 'yyyy-MM-dd')
        self.assertEqual(result, '2022-01-01')
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试 format_microsecond_timestamp
        result = format_microsecond_timestamp(self.timestamp_2022, 'yyyy-MM-dd HH:mm')
        self.assertEqual(result, '2022-01-01 08:00')
        
        # 测试 get_current_formatted_time
        current_time = get_current_formatted_time('yyyy-MM-dd')
        self.assertIsNotNone(current_time)
        self.assertRegex(current_time, r'\d{4}-\d{2}-\d{2}')
    
    def test_validate_timestamp(self):
        """测试时间戳验证"""
        # 有效时间戳
        self.assertTrue(TimeFormatter.validate_timestamp(self.timestamp_2022))
        self.assertTrue(TimeFormatter.validate_timestamp(self.timestamp_str))
        
        # 无效时间戳
        self.assertFalse(TimeFormatter.validate_timestamp('invalid'))
        self.assertFalse(TimeFormatter.validate_timestamp(None))
        self.assertFalse(TimeFormatter.validate_timestamp(-1))
        self.assertFalse(TimeFormatter.validate_timestamp(9999999999999999999))
    
    def test_error_handling(self):
        """测试错误处理"""
        # 无效输入应该返回None
        self.assertIsNone(TimeFormatter.format_timestamp('invalid', 'yyyy-MM-dd'))
        self.assertIsNone(TimeFormatter.format_timestamp(None, 'yyyy-MM-dd'))
        self.assertIsNone(TimeFormatter.format_timestamp('', 'yyyy-MM-dd'))
    
    def test_supported_formats(self):
        """测试支持的格式列表"""
        formats = TimeFormatter.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertGreater(len(formats), 0)
        self.assertIn('yyyy-MM-dd HH:mm:ss', formats)
        self.assertIn('yyyy年MM月dd日', formats)
    
    def test_format_conversion(self):
        """测试格式转换功能"""
        # 测试预定义格式
        result = TimeFormatter._convert_format('yyyy-MM-dd HH:mm:ss')
        self.assertEqual(result, '%Y-%m-%d %H:%M:%S')
        
        # 测试自定义格式转换
        result = TimeFormatter._convert_format('yyyy/MM/dd')
        self.assertEqual(result, '%Y/%m/%d')
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试最小有效时间戳（1970年）
        min_timestamp = 0  # 1970-01-01 00:00:00 UTC
        result = TimeFormatter.format_timestamp(min_timestamp, 'yyyy-MM-dd')
        self.assertIsNotNone(result)
        
        # 测试较大的时间戳
        large_timestamp = 4102444800000000  # 2100年左右
        result = TimeFormatter.format_timestamp(large_timestamp, 'yyyy-MM-dd')
        self.assertIsNotNone(result)
    
    def test_millisecond_vs_microsecond(self):
        """测试毫秒和微秒时间戳的区别"""
        # 毫秒时间戳（13位）
        millisecond_timestamp = 1640995200000  # 2022-01-01 08:00:00
        
        # 微秒时间戳（16位）
        microsecond_timestamp = 1640995200000000  # 2022-01-01 08:00:00
        
        # 微秒时间戳应该正常工作
        result_micro = TimeFormatter.format_timestamp(microsecond_timestamp, 'yyyy-MM-dd')
        self.assertEqual(result_micro, '2022-01-01')
        
        # 毫秒时间戳需要转换为微秒
        result_milli = TimeFormatter.format_timestamp(millisecond_timestamp * 1000, 'yyyy-MM-dd')
        self.assertEqual(result_milli, '2022-01-01')
    
    def test_chinese_formats(self):
        """测试中文格式"""
        chinese_formats = [
            ('yyyy年MM月dd日', '2022年01月01日'),
            ('yyyy年MM月dd日 HH:mm', '2022年01月01日 08:00'),
            ('MM月dd日', '01月01日'),
        ]
        
        for format_str, expected in chinese_formats:
            with self.subTest(format=format_str):
                result = TimeFormatter.format_timestamp(self.timestamp_2022, format_str)
                self.assertEqual(result, expected)


class TestTimeFormatterIntegration(unittest.TestCase):
    """时间格式化工具集成测试"""
    
    def test_batch_processing(self):
        """测试批量处理"""
        timestamps = [
            1640995200000000,  # 2022-01-01
            1641081600000000,  # 2022-01-02
            1641168000000000,  # 2022-01-03
        ]
        
        results = []
        for ts in timestamps:
            result = TimeFormatter.format_timestamp(ts, 'yyyy-MM-dd')
            results.append(result)
        
        expected = ['2022-01-01', '2022-01-02', '2022-01-03']
        self.assertEqual(results, expected)
    
    def test_feishu_integration_simulation(self):
        """模拟飞书集成测试"""
        # 模拟飞书API返回的数据
        feishu_data = {
            'created_time': '1640995200000000',
            'updated_time': 1641081600000000,
            'deleted_time': None,
        }
        
        # 模拟字段格式配置
        field_formatters = {
            'created_time': 'yyyy-MM-dd HH:mm',
            'updated_time': 'yyyy/MM/dd',
            'deleted_time': 'yyyy-MM-dd HH:mm:ss',
        }
        
        results = {}
        for field, timestamp in feishu_data.items():
            if timestamp is not None:
                formatter = field_formatters.get(field, 'yyyy-MM-dd HH:mm:ss')
                formatted = TimeFormatter.format_timestamp(timestamp, formatter)
                results[field] = formatted
            else:
                results[field] = None
        
        # 验证结果
        self.assertEqual(results['created_time'], '2022-01-01 08:00')
        self.assertEqual(results['updated_time'], '2022/01/02')
        self.assertIsNone(results['deleted_time'])


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)