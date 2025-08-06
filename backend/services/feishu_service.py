"""
飞书API服务类
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import Dict, List, Optional
from config import config

class FeishuService:
    """飞书API服务类"""
    
    def __init__(self):
        self.base_url = config.FEISHU_API_BASE_URL
        self.app_token = config.MASTER_APP_TOKEN
        self.personal_token = config.MASTER_PERSONAL_BASE_TOKEN
        self.table_id = config.MASTER_TABLE_ID
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.personal_token}',
            'Content-Type': 'application/json'
        }
    
    def get_table_records(self, table_id: Optional[str] = None, page_size: int = 20) -> Dict:
        """
        获取表格记录
        
        Args:
            table_id: 表格ID，如果不提供则使用默认的MASTER_TABLE_ID
            page_size: 每页记录数
            
        Returns:
            包含记录数据的字典
        """
        if not table_id:
            table_id = self.table_id
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        
        params = {
            'page_size': page_size
        }
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                return {
                    'success': True,
                    'data': data.get('data', {}),
                    'message': 'success'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': data.get('msg', '未知错误')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'data': None,
                'message': f'请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'处理失败: {str(e)}'
            }
    
    def get_record_by_id(self, record_id: str, table_id: Optional[str] = None) -> Dict:
        """
        根据记录ID获取单条记录

        Args:
            record_id: 记录ID
            table_id: 表格ID，如果不提供则使用默认的MASTER_TABLE_ID

        Returns:
            包含记录数据的字典
        """
        if not table_id:
            table_id = self.table_id

        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            if data.get('code') == 0:
                return {
                    'success': True,
                    'data': data.get('data', {}),
                    'message': 'success'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': data.get('msg', '未知错误')
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'data': None,
                'message': f'请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'处理失败: {str(e)}'
            }

    def get_farmer_list(self) -> Dict:
        """
        获取农户列表

        Returns:
            包含农户列表的字典
        """
        result = self.get_table_records()

        if not result['success']:
            return result

        # 处理农户数据
        farmers = []
        items = result['data'].get('items', [])

        for item in items:
            fields = item.get('fields', {})
            farmer_data = {
                'record_id': item.get('record_id'),
                'farmer_name': fields.get('农户', ''),
                'app_token': fields.get('app_token', ''),
                'auth_code': fields.get('授权码', ''),
                'created_time': item.get('created_time'),
                'last_modified_time': item.get('last_modified_time')
            }
            farmers.append(farmer_data)

        return {
            'success': True,
            'data': {
                'farmers': farmers,
                'total': result['data'].get('total', 0),
                'has_more': result['data'].get('has_more', False)
            },
            'message': 'success'
        }

    def get_farmer_by_id(self, farmer_id: str) -> Dict:
        """
        根据农户ID获取农户详情

        Args:
            farmer_id: 农户记录ID

        Returns:
            包含农户详情的字典
        """
        result = self.get_record_by_id(farmer_id)

        if not result['success']:
            return result

        # 处理农户详情数据
        record = result['data'].get('record', {})
        fields = record.get('fields', {})

        farmer_detail = {
            'record_id': record.get('record_id'),
            'farmer_name': fields.get('农户', ''),
            'app_token': fields.get('app_token', ''),
            'auth_code': fields.get('授权码', ''),
            'contact': fields.get('联系方式', ''),
            'address': fields.get('地址', ''),
            'created_time': record.get('created_time'),
            'last_modified_time': record.get('last_modified_time'),
            'created_by': record.get('created_by'),
            'last_modified_by': record.get('last_modified_by')
        }

        return {
            'success': True,
            'data': farmer_detail,
            'message': 'success'
        }

    def get_tables_by_farmer_token(self, farmer_app_token: str, farmer_auth_code: str) -> Dict:
        """
        使用农户的app_token和授权码获取数据表列表

        Args:
            farmer_app_token: 农户的app_token
            farmer_auth_code: 农户的授权码

        Returns:
            包含数据表列表的字典
        """
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{farmer_app_token}/tables"

        # 使用农户的授权码构建请求头
        headers = {
            'Authorization': f'Bearer {farmer_auth_code}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data.get('code') == 0:
                return {
                    'success': True,
                    'data': data.get('data', {}),
                    'message': 'success'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': data.get('msg', '未知错误')
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'data': None,
                'message': f'请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'处理失败: {str(e)}'
            }

    def get_farmer_tables(self, product_id: str) -> Dict:
        """
        根据产品ID获取农户的数据表列表

        Args:
            product_id: 产品ID（农户记录ID）

        Returns:
            包含农户数据表列表的字典
        """
        # 首先获取农户信息
        farmer_result = self.get_farmer_by_id(product_id)

        if not farmer_result['success']:
            return farmer_result

        farmer_data = farmer_result['data']

        # 检查农户是否有必要的API配置
        app_token = farmer_data.get('app_token', '').strip()
        auth_code = farmer_data.get('auth_code', '').strip()

        if not app_token or not auth_code:
            return {
                'success': False,
                'data': None,
                'message': '农户缺少必要的API配置信息（app_token或授权码）'
            }

        # 获取农户的数据表列表
        tables_result = self.get_tables_by_farmer_token(app_token, auth_code)

        if not tables_result['success']:
            return tables_result

        # 处理数据表信息
        tables_data = tables_result['data']
        tables = []

        for table in tables_data.get('items', []):
            table_info = {
                'table_id': table.get('table_id'),
                'table_name': table.get('name'),
                'revision': table.get('revision')
            }
            tables.append(table_info)

        return {
            'success': True,
            'data': {
                'farmer_info': {
                    'product_id': farmer_data['record_id'],
                    'farmer_name': farmer_data['farmer_name'],
                    'app_token': app_token,
                    'auth_code': auth_code
                },
                'tables': tables,
                'total': len(tables),
                'has_more': tables_data.get('has_more', False),
                'page_token': tables_data.get('page_token')
            },
            'message': 'success'
        }

# 创建服务实例
feishu_service = FeishuService()
