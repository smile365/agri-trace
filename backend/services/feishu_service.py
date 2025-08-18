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
        self.app_token = config.APP_TOKEN
        self.personal_token = config.PERSONAL_BASE_TOKEN
        
        # 新增飞书多维表格配置
        self.personal_base_token = config.PERSONAL_BASE_TOKEN
        self.app_token_new = config.APP_TOKEN
        
        # 数据表缓存
        self.tables_cache = {}
        
        # 自定义数据表处理器注册表
        self._custom_processors = {}
        
        # 初始化时获取数据表列表并缓存
        self._init_tables_cache()
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.personal_token}',
            'Content-Type': 'application/json'
        }
        
    def _get_headers_new(self) -> Dict[str, str]:
        """获取新的请求头（使用PERSONAL_BASE_TOKEN）"""
        return {
            'Authorization': f'Bearer {self.personal_base_token}',
            'Content-Type': 'application/json'
        }
        
    def _init_tables_cache(self):
        """初始化数据表缓存"""
        try:
            # 从飞书接口获取数据表列表
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token_new}/tables"
            response = requests.get(url, headers=self._get_headers_new())
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
                        
                print(f"成功缓存 {len(self.tables_cache)} 个数据表信息")
            else:
                print(f"获取数据表列表失败: {data.get('msg', '未知错误')}")
        except Exception as e:
            print(f"初始化数据表缓存异常: {str(e)}")
            
    def get_table_id_by_name(self, table_name: str) -> str:
        """根据表名获取表ID"""
        return self.tables_cache.get(table_name, '')
        
    def get_table_records_new(self, table_name: str) -> Dict:
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
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token_new}/tables/{table_id}/records"
        
        try:
            response = requests.get(url, headers=self._get_headers_new())
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
            
    def get_record_by_id_new(self, table_name: str, record_id: str) -> Dict:
        """根据记录ID查询记录详情（使用新的飞书多维表格接口）
        
        Args:
            table_name: 表名
            record_id: 记录ID
            
        Returns:
            包含记录详情的字典
        """
        # 从缓存中获取表ID
        table_id = self.get_table_id_by_name(table_name)
        if not table_id:
            return {
                'success': False,
                'data': None,
                'message': f'未找到表名为 {table_name} 的数据表'
            }
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token_new}/tables/{table_id}/records/{record_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers_new())
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
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'处理失败: {str(e)}'
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

    def get_farmer_table_records(self, farmer_app_token: str, farmer_auth_code: str, table_id: str, page_size: int = 20) -> Dict:
        """
        使用农户的app_token和授权码获取指定数据表的记录

        Args:
            farmer_app_token: 农户的app_token
            farmer_auth_code: 农户的授权码
            table_id: 数据表ID
            page_size: 每页记录数

        Returns:
            包含数据表记录的字典
        """
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{farmer_app_token}/tables/{table_id}/records"

        # 使用农户的授权码构建请求头
        headers = {
            'Authorization': f'Bearer {farmer_auth_code}',
            'Content-Type': 'application/json'
        }

        params = {
            'page_size': page_size
        }

        try:
            response = requests.get(url, headers=headers, params=params)
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

    def _process_product_table(self, records: List[Dict]) -> Dict:
        """
        处理商品表数据

        Args:
            records: 商品表记录列表

        Returns:
            处理后的商品信息字典
        """
        product_data = {}
        grouped_items = {}  # 存储分组数据

        for record in records:
            fields = record.get('fields', {})
            name = fields.get('名称', '')
            group = fields.get('分组', '').strip()
            text = fields.get('文本', '')
            image = fields.get('图片', [])
            order = fields.get('顺序', 0)

            # 确保图片是列表格式
            if not isinstance(image, list):
                image = []

            # 提取图片值的辅助函数
            def get_image_value(images):
                if images and len(images) > 0:
                    # 如果图片是字典格式，提取URL或文件信息
                    img = images[0]
                    if isinstance(img, dict):
                        return img.get('url', img.get('tmp_url', img.get('name', img)))
                    else:
                        return img
                return ''

            # 根据分组字段是否为空进行不同处理
            if group:
                # 分组不为空：组合成列表格式
                if group not in grouped_items:
                    grouped_items[group] = []

                # 构建分组项数据
                # 优先取文本，文本为空取图片，都为空则为空
                if text:
                    value = text
                elif image:
                    value = get_image_value(image)
                else:
                    value = ''

                item_data = {
                    'index': len(grouped_items[group]) + 1,
                    name: value
                }

                # 添加排序信息用于后续排序
                item_data['_order'] = order if isinstance(order, (int, float)) else 999

                grouped_items[group].append(item_data)
            else:
                # 分组为空：直接组合成键值对
                if name:
                    # 优先取文本，文本为空取图片，都为空则为空
                    if text:
                        value = text
                    elif image:
                        # 对于图片字段，保持原始格式以便前端处理
                        value = image[0] if image else ''
                    else:
                        value = ''

                    product_data[name] = value

        # 处理分组数据：按顺序排序并重新分配index
        for group_name, items in grouped_items.items():
            # 按顺序字段排序
            items.sort(key=lambda x: x.get('_order', 999))

            # 重新分配index并移除临时排序字段
            for i, item in enumerate(items, 1):
                item['index'] = i
                if '_order' in item:
                    del item['_order']

            # 将分组数据添加到产品数据中
            product_data[group_name] = items

        return product_data

    def _process_feeding_records_table(self, records: List[Dict]) -> List[Dict]:
        """
        处理饲喂记录表数据

        Args:
            records: 饲喂记录表记录列表

        Returns:
            处理后的饲喂记录列表
        """
        feeding_records = []
        for record in records:
            fields = record.get('fields', {})
            feeding_record = {
                'record_id': record.get('record_id'),
                'food_name': fields.get('名称', ''),
                'operator': fields.get('操作人', ''),
                'operation_time': fields.get('操作时间'),
                'created_time': fields.get('创建'),
                'updated_time': fields.get('更新'),
                'images': fields.get('图片', []) if isinstance(fields.get('图片'), list) else [],
                'description': fields.get('描述', ''),
                'amount': fields.get('用量', ''),
                'location': fields.get('位置', '')
            }
            feeding_records.append(feeding_record)

        return feeding_records

    def _process_breeding_process_table(self, records: List[Dict]) -> List[Dict]:
        """
        处理养殖流程表数据

        Args:
            records: 养殖流程表记录列表

        Returns:
            处理后的养殖流程列表
        """
        breeding_process = []
        for record in records:
            fields = record.get('fields', {})
            process_record = {
                'record_id': record.get('record_id'),
                'process_name': fields.get('名称', ''),
                'operation_time': fields.get('操作时间'),
                'created_time': fields.get('创建'),
                'updated_time': fields.get('更新'),
                'images': fields.get('图片', []) if isinstance(fields.get('图片'), list) else [],
                'description': fields.get('描述', ''),
                'status': fields.get('状态', ''),
                'operator': fields.get('操作人', ''),
                'location': fields.get('位置', '')
            }
            breeding_process.append(process_record)

        return breeding_process

    def _process_unknown_table(self, table_name: str, records: List[Dict]) -> List[Dict]:
        """
        处理未知类型的数据表

        Args:
            table_name: 数据表名称
            records: 记录列表

        Returns:
            处理后的记录列表
        """
        processed_records = []
        for record in records:
            fields = record.get('fields', {})
            processed_record = {
                'record_id': record.get('record_id'),
                'table_name': table_name,
                'fields': fields,
                'created_time': record.get('created_time'),
                'last_modified_time': record.get('last_modified_time')
            }
            processed_records.append(processed_record)

        return processed_records

    def register_table_processor(self, table_name: str, processor_func):
        """
        注册自定义数据表处理器

        Args:
            table_name: 数据表名称
            processor_func: 处理器函数，接收records参数，返回处理后的数据
        """
        self._custom_processors[table_name] = processor_func

    def unregister_table_processor(self, table_name: str):
        """
        取消注册数据表处理器

        Args:
            table_name: 数据表名称
        """
        if table_name in self._custom_processors:
            del self._custom_processors[table_name]

    def get_registered_processors(self) -> Dict:
        """
        获取所有已注册的处理器

        Returns:
            处理器字典
        """
        built_in_processors = {
            '商品': self._process_product_table,
            '饲喂记录': self._process_feeding_records_table,
            '养殖流程': self._process_breeding_process_table,
            'product': self._process_product_table,
            'feeding': self._process_feeding_records_table,
            'breeding': self._process_breeding_process_table
        }

        # 合并内置处理器和自定义处理器
        all_processors = built_in_processors.copy()
        all_processors.update(self._custom_processors)

        return all_processors

    def _get_table_processor(self, table_name: str):
        """
        获取数据表处理器

        Args:
            table_name: 数据表名称

        Returns:
            对应的处理器方法
        """
        # 获取所有已注册的处理器
        all_processors = self.get_registered_processors()
        return all_processors.get(table_name)

    def _is_known_table(self, table_name: str) -> bool:
        """
        检查是否为已知的数据表类型

        Args:
            table_name: 数据表名称

        Returns:
            是否为已知类型
        """
        all_processors = self.get_registered_processors()
        return table_name in all_processors

    def _calculate_statistics(self, complete_info: Dict) -> Dict:
        """
        计算统计信息

        Args:
            complete_info: 完整信息字典

        Returns:
            统计信息字典
        """
        statistics = {
            'feeding_count': len(complete_info.get('feeding_records', [])),
            'process_count': len(complete_info.get('breeding_process', [])),
            'product_fields_count': len(complete_info.get('product_info', {})),
            'other_tables_count': 0,
            'total_records': 0
        }

        # 计算其他表的记录数
        other_tables = complete_info.get('other_tables', {})
        for table_name, records in other_tables.items():
            statistics['other_tables_count'] += len(records)

        # 计算总记录数
        statistics['total_records'] = (
            statistics['feeding_count'] +
            statistics['process_count'] +
            statistics['other_tables_count']
        )

        return statistics

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
                'breeding_process': []
            }
            
            # 从「传感器」表获取传感器数据
            sensor_result = self.get_table_records_new('传感器')
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
            farmer_result = self.get_record_by_id_new('农户管理', product_id)
            print(json.dumps(farmer_result))
            if farmer_result['success']:
                # 更新产品信息
                complete_info['product_info'] = farmer_result['data'].get('fields', {})
            
            # 从「饲喂记录」表获取饲喂记录
            feeding_result = self.get_table_records_new('饲喂记录')
            if feeding_result['success']:
                feeding_records = feeding_result['data'].get('items', [])
                
                # 处理饲喂记录
                for record in feeding_records:
                    fields = record.get('fields', {})
                    farmer_link = fields.get('农户', [])
                    
                    # 检查是否与当前农户关联
                    if farmer_link and isinstance(farmer_link, list) and len(farmer_link) > 0:
                        record_ids = farmer_link[0].get('record_ids', [])
                        if product_id in record_ids:
                            feeding_record = {
                                'record_id': record.get('record_id'),
                                'food_name': fields.get('食物', ''),
                                'operator': fields.get('操作人', ''),
                                'operation_time': fields.get('操作时间'),
                                'created_time': fields.get('创建'),
                                'updated_time': fields.get('更新')
                            }
                            complete_info['feeding_records'].append(feeding_record)
            
            # 从「养殖流程」表获取养殖流程
            breeding_result = self.get_table_records_new('养殖流程')
            if breeding_result['success']:
                breeding_records = breeding_result['data'].get('items', [])
                
                # 处理养殖流程
                for record in breeding_records:
                    fields = record.get('fields', {})
                    farmer_link = fields.get('农户', [])
                    
                    # 检查是否与当前农户关联
                    if farmer_link and isinstance(farmer_link, list) and len(farmer_link) > 0:
                        record_ids = farmer_link[0].get('record_ids', [])
                        if product_id in record_ids:
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
            
            # 计算统计信息
            complete_info['statistics'] = self._calculate_statistics(complete_info)
            
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

    def get_table_fields(self, farmer_app_token: str, farmer_auth_code: str, table_id: str) -> Dict:
        """
        使用农户的app_token和授权码获取指定数据表的字段定义

        Args:
            farmer_app_token: 农户的app_token
            farmer_auth_code: 农户的授权码
            table_id: 数据表ID

        Returns:
            包含字段定义的字典
        """
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{farmer_app_token}/tables/{table_id}/fields"

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

    def get_table_fields_by_name(self, product_id: str, table_name: str) -> Dict:
        """
        根据产品ID和表名获取数据表的字段定义

        Args:
            product_id: 产品ID（农户记录ID）
            table_name: 数据表名称

        Returns:
            包含字段定义的字典
        """
        # 首先获取农户信息和数据表列表
        tables_result = self.get_farmer_tables(product_id)

        if not tables_result['success']:
            return tables_result

        farmer_info = tables_result['data']['farmer_info']
        tables = tables_result['data']['tables']

        # 查找指定名称的数据表
        target_table = None
        for table in tables:
            if table['table_name'] == table_name:
                target_table = table
                break

        if not target_table:
            return {
                'success': False,
                'data': None,
                'message': f'未找到名称为 "{table_name}" 的数据表'
            }

        app_token = farmer_info['app_token']
        auth_code = farmer_info['auth_code']
        table_id = target_table['table_id']

        # 获取字段定义
        fields_result = self.get_table_fields(app_token, auth_code, table_id)

        if not fields_result['success']:
            return fields_result

        # 处理字段定义数据
        fields_data = fields_result['data']
        fields = []

        for field in fields_data.get('items', []):
            field_info = {
                'field_id': field.get('field_id'),
                'field_name': field.get('field_name'),
                'type': field.get('type'),
                'property': field.get('property', {}),
                'description': field.get('description', ''),
                'is_primary': field.get('is_primary', False)
            }
            fields.append(field_info)

        return {
            'success': True,
            'data': {
                'table_info': {
                    'table_id': target_table['table_id'],
                    'table_name': target_table['table_name'],
                    'revision': target_table['revision']
                },
                'farmer_info': {
                    'product_id': farmer_info['product_id'],
                    'farmer_name': farmer_info['farmer_name']
                },
                'fields': fields,
                'total': len(fields),
                'has_more': fields_data.get('has_more', False),
                'page_token': fields_data.get('page_token')
            },
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
            
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{self.app_token_new}/tables/{table_id}/records/batch_update"
        
        payload = {
            "records": records
        }
        
        try:
            response = requests.post(url, headers=self._get_headers_new(), json=payload)
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

# 创建服务实例
feishu_service = FeishuService()
