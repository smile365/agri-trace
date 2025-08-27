"""多租户功能测试模块

测试缓存操作、飞书API调用、多租户数据隔离等功能
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch, MagicMock
from services.cache_service import MultiTenantCacheService
from services.tenant_service import TenantService
from services.feishu_service import FeishuService

class TestMultiTenantCache(unittest.TestCase):
    """多租户缓存功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.cache_service = MultiTenantCacheService()
        
    def test_cache_tenant_info(self):
        """测试租户信息缓存"""
        tenant_data = {
            'tenant_num': 'T001',
            'tenant_name': '测试租户',
            'app_token': 'test_app_token',
            'personal_base_token': 'test_personal_token',
            'authorized_count': 10
        }
        
        # 测试缓存租户信息
        result = self.cache_service.cache_tenant_info('T001', tenant_data)
        self.assertTrue(result)
        
        # 测试获取租户信息
        cached_data = self.cache_service.get_tenant_info('T001')
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['tenant_name'], '测试租户')
        
    def test_cache_tenant_tables(self):
        """测试租户表信息缓存"""
        tables_data = [
            {'table_name': '农户管理', 'table_id': 'tbl001'},
            {'table_name': '产品信息', 'table_id': 'tbl002'}
        ]
        
        # 测试缓存表信息
        result = self.cache_service.cache_tenant_tables('T001', tables_data)
        self.assertTrue(result)
        
        # 测试获取表信息
        cached_tables = self.cache_service.get_tenant_tables('T001')
        self.assertIsNotNone(cached_tables)
        self.assertEqual(len(cached_tables), 2)
        
    def test_cache_farmer_ids(self):
        """测试农户ID列表缓存"""
        farmer_ids = ['farmer001', 'farmer002', 'farmer003']
        
        # 测试缓存农户ID列表
        result = self.cache_service.cache_farmer_ids('T001', farmer_ids, 10)
        self.assertTrue(result)
        
        # 测试获取农户ID列表
        cached_data = self.cache_service.get_farmer_ids('T001')
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data['farmer_ids']), 3)
        
        # 测试农户授权验证
        self.assertTrue(self.cache_service.is_farmer_authorized('T001', 'farmer001'))
        self.assertFalse(self.cache_service.is_farmer_authorized('T001', 'farmer999'))
        
    def test_clear_tenant_cache(self):
        """测试清除租户缓存"""
        # 先添加一些缓存数据
        tenant_data = {'tenant_num': 'T001', 'tenant_name': '测试租户'}
        self.cache_service.cache_tenant_info('T001', tenant_data)
        
        # 验证数据存在
        self.assertIsNotNone(self.cache_service.get_tenant_info('T001'))
        
        # 清除缓存
        result = self.cache_service.clear_tenant_cache('T001')
        self.assertTrue(result)
        
        # 验证数据已清除
        self.assertIsNone(self.cache_service.get_tenant_info('T001'))

class TestTenantService(unittest.TestCase):
    """租户服务功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.tenant_service = TenantService()
        
    @patch('services.tenant_service.FeishuService')
    def test_init_system_feishu_service(self, mock_feishu):
        """测试系统级飞书服务初始化"""
        # 模拟配置
        self.tenant_service.sys_app_token = 'test_sys_app_token'
        self.tenant_service.sys_personal_base_token = 'test_sys_personal_token'
        
        # 测试初始化
        result = self.tenant_service._init_system_feishu_service()
        self.assertTrue(result)
        self.assertIsNotNone(self.tenant_service.system_feishu_service)
        
    @patch('requests.get')
    def test_load_tenant_tables(self, mock_get):
        """测试加载租户表信息"""
        # 模拟租户信息
        tenant_info = {
            'app_token': 'test_app_token',
            'personal_base_token': 'test_personal_token'
        }
        
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'items': [
                    {'name': '农户管理', 'table_id': 'tbl001'},
                    {'name': '产品信息', 'table_id': 'tbl002'}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 模拟缓存服务
        with patch.object(self.tenant_service.cache_service, 'get_tenant_info', return_value=tenant_info), \
             patch.object(self.tenant_service.cache_service, 'cache_tenant_tables', return_value=True):
            
            result = self.tenant_service.load_tenant_tables('T001')
            self.assertTrue(result)
            
    def test_validate_farmer_access(self):
        """测试农户访问权限验证"""
        # 模拟缓存服务返回值
        with patch.object(self.tenant_service.cache_service, 'is_farmer_authorized', return_value=True):
            result = self.tenant_service.validate_farmer_access('T001', 'farmer001')
            self.assertTrue(result)
            
        with patch.object(self.tenant_service.cache_service, 'is_farmer_authorized', return_value=False):
            result = self.tenant_service.validate_farmer_access('T001', 'farmer999')
            self.assertFalse(result)
            
    @patch('services.tenant_service.FeishuService')
    def test_get_tenant_farm_info(self, mock_feishu_class):
        """测试获取租户农户信息"""
        # 模拟租户信息
        tenant_info = {
            'app_token': 'test_app_token',
            'personal_base_token': 'test_personal_token'
        }
        
        # 模拟飞书服务
        mock_feishu_instance = Mock()
        mock_feishu_instance.get_farm_complete_info.return_value = {
            'success': True,
            'data': {'farmer_name': '测试农户'},
            'message': 'success'
        }
        mock_feishu_class.return_value = mock_feishu_instance
        
        # 模拟缓存服务
        with patch.object(self.tenant_service.cache_service, 'get_tenant_info', return_value=tenant_info):
            result = self.tenant_service.get_tenant_farm_info('T001', 'farmer001')
            
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['data'])
            
class TestFeishuServiceMultiTenant(unittest.TestCase):
    """飞书服务多租户功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.feishu_service = FeishuService()
        
    def test_init_with_custom_tokens(self):
        """测试使用自定义token初始化"""
        custom_app_token = 'custom_app_token'
        custom_personal_token = 'custom_personal_token'
        
        service = FeishuService(app_token=custom_app_token, personal_base_token=custom_personal_token)
        
        self.assertEqual(service.app_token_new, custom_app_token)
        self.assertEqual(service.personal_base_token, custom_personal_token)
        
    @patch('requests.get')
    def test_get_record_by_id(self, mock_get):
        """测试根据ID获取记录"""
        # 模拟表名缓存
        self.feishu_service.tables_cache = {'测试表': 'tbl001'}
        
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'record': {
                    'record_id': 'rec001',
                    'fields': {'name': '测试记录'}
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.feishu_service.get_record_by_id('测试表', 'rec001')
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        
    @patch('requests.get')
    def test_get_tables_list(self, mock_get):
        """测试获取表列表"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'items': [
                    {'name': '农户管理', 'table_id': 'tbl001'},
                    {'name': '产品信息', 'table_id': 'tbl002'}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.feishu_service.get_tables_list()
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['items']), 2)

class TestMultiTenantIntegration(unittest.TestCase):
    """多租户功能集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.tenant_service = TenantService()
        
    def test_tenant_data_isolation(self):
        """测试租户数据隔离"""
        # 模拟两个不同租户的数据
        tenant1_data = {
            'tenant_num': 'T001',
            'tenant_name': '租户1',
            'app_token': 'app_token_1',
            'personal_base_token': 'personal_token_1'
        }
        
        tenant2_data = {
            'tenant_num': 'T002', 
            'tenant_name': '租户2',
            'app_token': 'app_token_2',
            'personal_base_token': 'personal_token_2'
        }
        
        # 缓存租户数据
        self.tenant_service.cache_service.cache_tenant_info('T001', tenant1_data)
        self.tenant_service.cache_service.cache_tenant_info('T002', tenant2_data)
        
        # 缓存不同的农户ID列表
        self.tenant_service.cache_service.cache_farmer_ids('T001', ['farmer001', 'farmer002'], 10)
        self.tenant_service.cache_service.cache_farmer_ids('T002', ['farmer003', 'farmer004'], 5)
        
        # 验证数据隔离
        self.assertTrue(self.tenant_service.validate_farmer_access('T001', 'farmer001'))
        self.assertFalse(self.tenant_service.validate_farmer_access('T001', 'farmer003'))
        
        self.assertTrue(self.tenant_service.validate_farmer_access('T002', 'farmer003'))
        self.assertFalse(self.tenant_service.validate_farmer_access('T002', 'farmer001'))
        
    def test_authorization_limit(self):
        """测试授权数量限制"""
        # 模拟租户数据，授权数量为2
        tenant_data = {
            'tenant_num': 'T001',
            'tenant_name': '测试租户',
            'authorized_count': 2
        }
        
        self.tenant_service.cache_service.cache_tenant_info('T001', tenant_data)
        
        # 缓存3个农户ID，但授权数量只有2
        farmer_ids = ['farmer001', 'farmer002', 'farmer003']
        self.tenant_service.cache_service.cache_farmer_ids('T001', farmer_ids, 2)
        
        # 验证前2个农户有权限
        self.assertTrue(self.tenant_service.validate_farmer_access('T001', 'farmer001'))
        self.assertTrue(self.tenant_service.validate_farmer_access('T001', 'farmer002'))
        
        # 验证第3个农户没有权限（超出授权数量）
        self.assertFalse(self.tenant_service.validate_farmer_access('T001', 'farmer003'))

if __name__ == '__main__':
    unittest.main()