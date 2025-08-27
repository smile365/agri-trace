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

    def __init__(self, app_token: str, personal_base_token: str ):
        self.base_url = config.FEISHU_API_BASE_URL
        self.app_token = app_token
        self.personal_base_token = personal_base_token
        if not app_token or not personal_base_token:
            raise ValueError(f"缺少必要的配置项: app_token={app_token}, personal_base_token={personal_base_token}")
        # 数据表缓存
        self.tables_cache = {}
        self.time_format_cache = {}
        # 初始化时获取数据表列表并缓存
        self._init_tables_cache()
        self._init_time_cache()
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.personal_base_token}',
            'Content-Type': 'application/json'
        }
        
        
    def _init_tables_cache(self):
        """初始化数据表缓存"""
        try:
            # 从飞书接口获取数据表列表
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                tables = data.get('data', {}).get('items', [])
                
                # 缓存数据表信息
                for table in tables:
                    table_name = table.get('name')
                    table_id = table.get('table_id')
                    if table_name and table_id:
                        self.tables_cache[table_name] = table_id
                        
                #print(f"成功缓存 {len(self.tables_cache)} 个数据表信息")
            else:
                print(f"获取数据表列表失败: {data.get('msg', '未知错误')}")
        except Exception as e:
            print(f"初始化数据表缓存异常: {str(e)}")
            
    def _init_time_cache(self):
        for name, table_id in self.tables_cache.items():
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                fields = data.get('data', {}).get('items', [])
                for field in fields:
                    if field.get('ui_type') == 'DateTime':
                        if not self.time_format_cache.get(name):
                            self.time_format_cache[name] = {}
                        self.time_format_cache[name][field.get('field_name')] = field.get('property').get('date_formatter')
                        #print(field)
            print(f'{name}:{self.time_format_cache.get(name)}')
        

    def get_table_id_by_name(self, table_name: str) -> str:
        """根据表名获取表ID"""
        return self.tables_cache.get(table_name, '')
        
    def get_table_records(self, table_name: str) -> Dict:
        """获取指定表名的记录
        
        Args:
            table_name: 表名
            
        Returns:
            包含记录数据的字典
        """
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return {
                'success': False,
                'data': None,
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        
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
    
    def get_table_records_filter(self, table_name: str, filter: str) -> Dict:
        """获取指定表名的记录（带过滤条件）
        
        Args:
            table_name: 表名
            filter: 过滤条件，例如 'CurrentValue.[农户]="张三"'
            
        Returns:
            包含记录数据的字典
        """
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return {
                'success': False,
                'data': None,
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records?filter={filter}"
        
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
            

    def get_farm_complete_info(self, product_id: str) -> Dict:
        """
        获取农户的完整信息，包括商品信息、饲喂记录、养殖流程等

        Args:
            product_id: 产品ID（农户记录ID）

        Returns:
            包含农户完整信息的字典
        """
        try:
            # 初始化结果数据
            complete_info = {
                'sensor': {},
                'product_info': {},
                'feeding_records': [],
                'breeding_process': [],
                'statistics': {}
            }
            
            # 从「传感器」表获取传感器数据
            sensor_result = self.get_table_records('传感器')
            if sensor_result['success']:
                sensor_records = sensor_result['data'].get('items', [])
                
                # 处理传感器数据，将其转换为 {'温度': '26.0', '湿度': '47.0', ...} 格式
                for record in sensor_records:
                    fields = record.get('fields', {})
                    sensor_name = fields.get('名称', '')
                    sensor_value = fields.get('文本', '') or fields.get('数值', '')
                    
                    if sensor_name and sensor_value:
                        complete_info['sensor'][sensor_name] = str(sensor_value)
            
            # 使用「根据记录ID查询记录详情」接口获取农户信息
            farmer_result = self.get_record_by_id('农户管理', product_id)
            #print(json.dumps(farmer_result))
            if farmer_result['success']:
                # 更新产品信息
                complete_info['product_info'] = farmer_result['data'].get('fields', {})
            farmer_name = complete_info['product_info'].get('饲养农户', '')
            # 从「饲喂记录」表获取饲喂记录
            filter_str = f'CurrentValue.[农户]="{farmer_name}"'
            feeding_result = self.get_table_records_filter('饲喂记录',filter_str)
            #print(json.dumps(feeding_result))
            if feeding_result['success']:
                feeding_records = feeding_result['data'].get('items', [])
                #print(json.dumps(feeding_records))
                # 处理饲喂记录
                complete_info['statistics']['feeding_count'] = len(feeding_records)
                for record in feeding_records:
                    fields = record.get('fields', {})
                    feeding_record = {
                        'record_id': record.get('record_id'),
                        'food_name': fields.get('食物', ''),
                        'operator': fields.get('操作人', ''),
                        'operation_time': fields.get('操作时间'),
                        'images': [f'/api/v1/img/{item["file_token"]}' for item in fields.get('图片', []) if isinstance(fields.get('图片'), list)],
                        'created_time': fields.get('创建'),
                        'updated_time': fields.get('更新')
                    }
                    complete_info['feeding_records'].append(feeding_record)
            
            # 从「养殖流程」表获取养殖流程
            breeding_result = self.get_table_records_filter('养殖流程',filter_str)
            if breeding_result['success']:
                breeding_records = breeding_result['data'].get('items', [])
                complete_info['statistics']['process_count'] = len(breeding_records)
                # 处理养殖流程
                for record in breeding_records:
                    fields = record.get('fields', {})
                    process_record = {
                        'record_id': record.get('record_id'),
                        'process_name': fields.get('流程', ''),
                        'operation_time': fields.get('操作时间'),
                        'created_time': fields.get('创建'),
                        'updated_time': fields.get('更新'),
                        'images': fields.get('图片', []) if isinstance(fields.get('图片'), list) else [],
                        'operator': fields.get('操作人', '')
                    }
                    complete_info['breeding_process'].append(process_record)
            
            
            return {
                'success': True,
                'data': complete_info,
                'message': 'success'
            }
            
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'获取农户完整信息失败: {str(e)}'
            }

    def batch_update_records(self, table_name: str, records: List[Dict]) -> Dict:
        """批量更新多条记录
        
        Args:
            table_name: 表名
            records: 要更新的记录列表，每个记录包含 record_id 和 fields
            
        Returns:
            包含更新结果的字典
        """
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return {
                'success': False,
                'data': None,
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch_update"
        
        payload = {
            "records": records
        }
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
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
    
    def get_record_by_id(self, table_name: str, record_id: str) -> Dict:
        """根据记录ID获取单条记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            
        Returns:
            包含记录数据的字典
        """
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return {
                'success': False,
                'data': None,
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0 and data.get('data'):
                return {
                    'success': True,
                    'data': data['data'].get('record', {}),
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
    
    def get_tables_list(self) -> Dict:
        """获取应用下的所有表列表
        
        Returns:
            包含表列表的字典
        """
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables"
        
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


