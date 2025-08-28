#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BDLot 内存缓存模块测试
测试 MemoryCache 和 URLRequestCache 类的各种功能
"""

import unittest
import time
import threading
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.bdlot import (
    MemoryCache,
    URLRequestCache,
    set_cache,
    get_cache,
    cache_url_request,
    get_latest_url_request,
    get_url_request_history
)


class TestMemoryCache(unittest.TestCase):
    """内存缓存基础功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.cache = MemoryCache()
    
    def test_set_and_get(self):
        """测试基本的设置和获取功能"""
        # 测试基本设置和获取
        self.assertTrue(self.cache.set("test_key", "test_value"))
        self.assertEqual(self.cache.get("test_key"), "test_value")
        
        # 测试不存在的键
        self.assertIsNone(self.cache.get("non_existent_key"))
    
    def test_expire_functionality(self):
        """测试过期功能"""
        # 设置1秒过期的缓存
        self.assertTrue(self.cache.set("expire_key", "expire_value", expire_seconds=1))
        
        # 立即获取应该成功
        self.assertEqual(self.cache.get("expire_key"), "expire_value")
        
        # 等待过期
        time.sleep(1.1)
        
        # 过期后应该返回None
        self.assertIsNone(self.cache.get("expire_key"))
    
    def test_delete_functionality(self):
        """测试删除功能"""
        # 设置缓存
        self.cache.set("delete_key", "delete_value")
        self.assertEqual(self.cache.get("delete_key"), "delete_value")
        
        # 删除缓存
        self.assertTrue(self.cache.delete("delete_key"))
        self.assertIsNone(self.cache.get("delete_key"))
    
    def test_exists_functionality(self):
        """测试存在性检查功能"""
        # 设置缓存
        self.cache.set("exists_key", "exists_value")
        
        # 检查存在性
        self.assertTrue(self.cache.exists("exists_key"))
        self.assertFalse(self.cache.exists("non_existent_key"))
        
        # 删除后检查
        self.cache.delete("exists_key")
        self.assertFalse(self.cache.exists("exists_key"))
    
    def test_clear_functionality(self):
        """测试清空功能"""
        # 设置多个缓存
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # 验证缓存存在
        self.assertEqual(self.cache.size(), 3)
        
        # 清空缓存
        self.assertTrue(self.cache.clear())
        self.assertEqual(self.cache.size(), 0)
    
    def test_keys_and_size(self):
        """测试键列表和大小功能"""
        # 设置多个缓存
        keys = ["key1", "key2", "key3"]
        for key in keys:
            self.cache.set(key, f"value_{key}")
        
        # 检查键列表
        cached_keys = self.cache.keys()
        self.assertEqual(len(cached_keys), 3)
        for key in keys:
            self.assertIn(key, cached_keys)
        
        # 检查大小
        self.assertEqual(self.cache.size(), 3)
    
    def test_cleanup_expired(self):
        """测试清理过期缓存功能"""
        # 设置一些缓存，部分会过期
        self.cache.set("permanent_key", "permanent_value")  # 永不过期
        self.cache.set("expire_key1", "expire_value1", expire_seconds=1)
        self.cache.set("expire_key2", "expire_value2", expire_seconds=1)
        
        # 等待过期
        time.sleep(1.1)
        
        # 清理过期缓存
        cleaned_count = self.cache.cleanup_expired()
        self.assertEqual(cleaned_count, 2)
        
        # 验证只剩下永不过期的缓存
        self.assertEqual(self.cache.size(), 1)
        self.assertTrue(self.cache.exists("permanent_key"))
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def worker(thread_id):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                self.cache.set(key, value)
                retrieved_value = self.cache.get(key)
                self.assertEqual(retrieved_value, value)
        
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有数据都正确存储
        self.assertEqual(self.cache.size(), 50)  # 5个线程 × 10个键


class TestURLRequestCache(unittest.TestCase):
    """URL 请求缓存功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.url_cache = URLRequestCache(max_size=5)
    
    def test_cache_request(self):
        """测试缓存请求功能"""
        # 缓存请求
        cache_key = self.url_cache.cache_request(
            "http://localhost:8080/api/test",
            "param1=value1&param2=value2"
        )
        
        # 验证缓存键格式
        self.assertTrue(cache_key.startswith("url_request_history_"))
        self.assertNotEqual(cache_key, "")
    
    def test_get_latest_request(self):
        """测试获取最新请求功能"""
        # 缓存请求
        test_url = "http://localhost:8080/api/latest"
        test_query = "id=123&name=test"
        
        self.url_cache.cache_request(test_url, test_query)
        
        # 获取最新请求
        latest_request = self.url_cache.get_latest_request()
        
        # 验证结果
        self.assertIsNotNone(latest_request)
        self.assertEqual(latest_request['url'], test_url)
        self.assertEqual(latest_request['query_string'], test_query)
        self.assertIn('timestamp', latest_request)
        self.assertIn('datetime', latest_request)
    
    def test_get_request_by_key(self):
        """测试根据键获取请求功能"""
        # 缓存请求
        test_url = "http://localhost:8080/api/bykey"
        test_query = "key=value"
        
        cache_key = self.url_cache.cache_request(test_url, test_query)
        
        # 根据键获取请求
        request_info = self.url_cache.get_request_by_key(cache_key)
        
        # 验证结果
        self.assertIsNotNone(request_info)
        self.assertEqual(request_info['url'], test_url)
        self.assertEqual(request_info['query_string'], test_query)
    
    def test_get_request_history(self):
        """测试获取请求历史功能"""
        # 缓存多个请求
        test_requests = [
            ("http://localhost:8080/api/test1", "param1=value1"),
            ("http://localhost:8080/api/test2", "param2=value2"),
            ("http://localhost:8080/api/test3", "param3=value3"),
        ]
        
        for url, query in test_requests:
            self.url_cache.cache_request(url, query)
            time.sleep(0.01)  # 确保时间戳不同
        
        # 获取历史记录
        history = self.url_cache.get_request_history(limit=5)
        
        # 验证结果
        self.assertEqual(len(history), 3)
        
        # 验证顺序（最新的在前）
        self.assertEqual(history[0]['url'], "http://localhost:8080/api/test3")
        self.assertEqual(history[1]['url'], "http://localhost:8080/api/test2")
        self.assertEqual(history[2]['url'], "http://localhost:8080/api/test1")
    
    def test_max_size_limit(self):
        """测试最大大小限制功能"""
        # 缓存超过最大大小的请求
        for i in range(10):  # 超过 max_size=5
            self.url_cache.cache_request(
                f"http://localhost:8080/api/test{i}",
                f"param{i}=value{i}"
            )
            time.sleep(0.01)
        
        # 获取历史记录
        history = self.url_cache.get_request_history(limit=20)
        
        # 验证只保留了最新的5条记录
        self.assertLessEqual(len(history), 5)
        
        # 验证保留的是最新的记录
        if len(history) == 5:
            self.assertEqual(history[0]['url'], "http://localhost:8080/api/test9")
            self.assertEqual(history[4]['url'], "http://localhost:8080/api/test5")
    
    def test_cache_stats(self):
        """测试缓存统计功能"""
        # 初始状态
        stats = self.url_cache.get_cache_stats()
        self.assertEqual(stats['history_count'], 0)
        self.assertFalse(stats['has_latest_request'])
        
        # 缓存一些请求
        for i in range(3):
            self.url_cache.cache_request(
                f"http://localhost:8080/api/stats{i}",
                f"param{i}=value{i}"
            )
        
        # 检查统计信息
        stats = self.url_cache.get_cache_stats()
        self.assertEqual(stats['history_count'], 3)
        self.assertTrue(stats['has_latest_request'])
        self.assertEqual(stats['max_size'], 5)
    
    def test_clear_all(self):
        """测试清空所有缓存功能"""
        # 缓存一些请求
        self.url_cache.cache_request("http://localhost:8080/api/clear1", "param1=value1")
        self.url_cache.cache_request("http://localhost:8080/api/clear2", "param2=value2")
        
        # 验证缓存存在
        stats = self.url_cache.get_cache_stats()
        self.assertGreater(stats['total_keys'], 0)
        
        # 清空缓存
        self.assertTrue(self.url_cache.clear_all())
        
        # 验证缓存已清空
        stats = self.url_cache.get_cache_stats()
        self.assertEqual(stats['total_keys'], 0)
        self.assertEqual(stats['history_count'], 0)
        self.assertFalse(stats['has_latest_request'])


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def test_global_cache_functions(self):
        """测试全局缓存便捷函数"""
        # 测试设置和获取
        self.assertTrue(set_cache("global_key", "global_value"))
        self.assertEqual(get_cache("global_key"), "global_value")
        
        # 测试不存在的键
        self.assertIsNone(get_cache("non_existent_global_key"))
    
    def test_url_request_functions(self):
        """测试 URL 请求便捷函数"""
        # 缓存请求
        test_url = "http://localhost:8080/api/convenience"
        test_query = "convenience=test"
        
        cache_key = cache_url_request(test_url, test_query)
        self.assertNotEqual(cache_key, "")
        
        # 获取最新请求
        latest_request = get_latest_url_request()
        self.assertIsNotNone(latest_request)
        self.assertEqual(latest_request['url'], test_url)
        self.assertEqual(latest_request['query_string'], test_query)
        
        # 获取请求历史
        history = get_url_request_history(5)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]['url'], test_url)


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_invalid_inputs(self):
        """测试无效输入处理"""
        cache = MemoryCache()
        
        # 测试空键
        self.assertTrue(cache.set("", "empty_key_value"))  # 空键应该被允许
        self.assertEqual(cache.get(""), "empty_key_value")
        
        # 测试空值
        self.assertTrue(cache.set("empty_value_key", ""))  # 空值应该被允许
        self.assertEqual(cache.get("empty_value_key"), "")
    
    def test_url_cache_invalid_inputs(self):
        """测试 URL 缓存无效输入处理"""
        url_cache = URLRequestCache()
        
        # 测试空 URL 和查询字符串
        cache_key = url_cache.cache_request("", "")
        self.assertNotEqual(cache_key, "")  # 应该仍然能够缓存
        
        # 获取不存在的键
        result = url_cache.get_request_by_key("non_existent_key")
        self.assertIsNone(result)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)