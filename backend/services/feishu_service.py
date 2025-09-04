"""
飞书API服务类
"""
from multiprocessing import Value
import sys
import os
from venv import logger

from urllib3 import fields
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import Dict, List, Optional
from config import config
from utils.time_formatter import TimeFormatter

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
        self.attachment_fields_cache = {}
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

    def get_table_fields(self, table_name: str) -> Dict:
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return []
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        data = response.json()
        if data.get('code') != 0:
            return []
        return data.get('data', {}).get('items', [])

    def _init_time_cache(self):
        for name in self.tables_cache.keys():
            fields = self.get_table_fields(name)
            for field in fields:
                
                if field.get('ui_type') == 'DateTime':
                    if not self.time_format_cache.get(name):
                        self.time_format_cache[name] = {}
                    self.time_format_cache[name][field.get('field_name')] = field.get('property').get('date_formatter')
                elif field.get('ui_type') == 'Attachment':
                    if not self.attachment_fields_cache.get(name):
                        self.attachment_fields_cache[name] = []
                    self.attachment_fields_cache[name].append(field.get('field_name'))
                    #print(field)
            print(f'time_format_cache,{name}:{self.time_format_cache.get(name)}')
            print(f'attachment_fields_cache,{name}:{self.attachment_fields_cache.get(name)}')
        

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
            if data.get('code') != 0 or not data.get('data'):
                return {
                    'success': False,
                    'data': None,
                    'message': data.get('msg', '未知错误')
                }
            # table_time_formater = self.time_format_cache.get(table_name)
            items = data.get('data').get('items')
            table_time_formater = self.time_format_cache.get(table_name)
            table_attachment_fields = self.attachment_fields_cache.get(table_name)
            records = []
            for item in items:
                records.append(self.format_record(item.get('fields'),table_time_formater, table_attachment_fields))
            return {
                'success': True,
                'data': records,
                'message': 'success'
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
            sensor_records = sensor_result.get('data',{}).get('items', [])
            
            # 处理传感器数据，将其转换为 {'温度': '26.0', '湿度': '47.0', ...} 格式
            for record in sensor_records:
                fields = record.get('fields', {})
                sensor_name = fields.get('名称', '')
                sensor_value = fields.get('数据', '') or fields.get('数值', '')
                
                if sensor_name and sensor_value:
                    complete_info['sensor'][sensor_name] = str(sensor_value)
        
        # 使用「根据记录ID查询记录详情」接口获取农户信息
        farmer_result = self.get_record_by_id('农户管理', product_id)
        if not farmer_result.get('data'):
            return {
                'success': False,
                'data': None,
                'message': f'未找到记录ID为 {product_id} 的农户信息'
            }
        complete_info['product_info'] = farmer_result['data']
        farmer_name = complete_info['product_info'].get('饲养农户', '')
        # 从「饲喂记录」表获取饲喂记录
        filter_str = f'CurrentValue.[农户]="{farmer_name}"'
        feeding_result = self.get_table_records_filter('饲喂记录',filter_str)
        #print(f'饲喂记录:{feeding_result}')
        if feeding_result['data']:
            feeding_records = feeding_result['data']
            complete_info['statistics']['feeding_count'] = len(feeding_records)
            for record in feeding_records:
                feeding_record = {
                    'food_name': record.get('食物', ''),
                    'operator': record.get('操作人', ''),
                    'operation_time': record.get('操作时间'),
                    'images': record.get('图片', []),
                    'created_time': record.get('创建'),
                    'updated_time': record.get('更新')
                }
                complete_info['feeding_records'].append(feeding_record)
            
        # 从「养殖流程」表获取养殖流程
        breeding_result = self.get_table_records_filter('养殖流程',filter_str)
        if breeding_result['success']:
            breeding_records = breeding_result['data']
            complete_info['statistics']['process_count'] = len(breeding_records)
            # 处理养殖流程
            for fields in breeding_records:
                process_record = {
                    'process_name': fields.get('流程', ''),
                    'operation_time': fields.get('操作时间'),
                    'created_time': fields.get('创建'),
                    'updated_time': fields.get('更新'),
                    'images': fields.get('图片', []),
                    'operator': fields.get('操作人', '')
                }
                complete_info['breeding_process'].append(process_record)
        
        
        return {
            'success': True,
            'data': complete_info,
            'message': 'success'
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
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            if not data.get('code') == 0 or not data.get('data'):
                logger.info(data)
                logger.info(f'url:{url}')
                logger.info(self._get_headers())
                return data
            table_time_formater = self.time_format_cache.get(table_name)
            table_attachment_fields = self.attachment_fields_cache.get(table_name)
            fields = data['data'].get('record',{}).get('fields',{})
            record = self.format_record(fields, table_time_formater,table_attachment_fields)
            return {
                'success': True,
                'data': record,
                'message': 'success'
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


    def format_record(self, fields: Dict, table_time_formater: Dict, table_attachment_fields: List) -> Dict:
        logger.debug(f"fields:{fields}, \n table_time_formater:{table_time_formater},  \n table_attachment_fields:{table_attachment_fields}")
        if not table_time_formater and not table_attachment_fields:
            return fields
        if not table_attachment_fields or len(table_attachment_fields) <1:
            return self._format_record_timestamp(fields,table_time_formater)
        for field_name in table_attachment_fields:
            value = fields.get(field_name)
            if value:
                fields[field_name] = self._format_record_attachment(value)
        return self._format_record_timestamp(fields,table_time_formater)

    def _format_record_attachment(self, images: List) -> List:
        processed_images = []
        for img in images:
            if isinstance(img, dict) and 'file_token' in img:
                file_token = img['file_token']
                if file_token:
                    processed_images.append(f"/api/v1/img/{file_token}")
        return processed_images

    def _format_record_timestamp(self, fields: Dict, table_time_formater: Dict) -> Dict:
        """格式化记录中的时间戳"""
        for field_name, time_format in table_time_formater.items():
            value = fields.get(field_name)
            fields[field_name] = TimeFormatter.format_timestamp(value, time_format)
            logger.info(f"{field_name}:{value}, {time_format}:{fields[field_name]} ")
        return fields


            
       