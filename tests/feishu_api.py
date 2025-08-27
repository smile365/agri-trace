import requests
import json
from typing import Dict, List, Optional, Any


class FeishuApi:
    """飞书多维表格API客户端"""
    
    def __init__(self, app_token: str, personal_token: str, base_url: str = "https://base-api.feishu.cn"):
        """
        初始化飞书API客户端
        
        Args:
            app_token: 应用token
            personal_token: 个人访问token
            base_url: API基础URL
        """
        self.app_token = app_token
        self.personal_token = personal_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {personal_token}",
            "Content-Type": "application/json"
        }
        # 缓存
        self._table_cache = {}  # {table_name: table_id}
        self._time_fmt_cache = {}  # {table_id: {field: time_fmt}}
        
        # 初始化时更新缓存
        self.update_cache()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求体数据
            params: 查询参数
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
    
    def _cache_tables(self) -> None:
        """
        缓存所有数据表 {table_name: table_id}
        """
        try:
            tables_response = self._list_tables()
            tables = tables_response.get('data', {}).get('items', [])
            self._table_cache = {table['name']: table['table_id'] for table in tables}
            # print(f"缓存数据表成功: {self._table_cache}")
        except Exception as e:
            print(f"缓存数据表失败: {e}")
    
    def _cache_time_fmt(self) -> None:
        """
        缓存所有数据表关于所有时间相关字段的格式化 {table_id: {field: time_fmt}}
        """
        try:
            # 确保表缓存已更新
            if not self._table_cache:
                self._cache_tables()
            
            for table_name, table_id in self._table_cache.items():
                fields_response = self._list_fields(table_id)
                fields = fields_response.get('data', {}).get('items', [])
                time_fields = {}
                for field in fields:
                    field_type = field.get('ui_type')
                    field_name = field.get('field_name')
                    
                    # 检查是否为时间相关字段
                    if field_type in ['DateTime', 'CreatedTime', 'ModifiedTime']:
                        # 获取时间格式，默认为标准格式
                        time_format = field.get('property', {}).get('date_format', 'yyyy/MM/dd HH:mm')
                        time_fields[field_name] = time_format
                
                if time_fields:
                    self._time_fmt_cache[table_id] = time_fields
                    
        except Exception as e:
            print(f"缓存时间格式失败: {e}")
    
    def _fmt_time(self, table_id: str, record: Dict) -> Dict:
         """
         对某一行记录中含日期的字段进行格式化
         
         Args:
             table_id: 数据表ID
             record: 记录数据
             
         Returns:
             格式化后的记录数据
         """
         try:
             # 确保时间格式缓存已更新
             if not self._time_fmt_cache:
                 self._cache_time_fmt()
             
             # 获取该表的时间字段格式信息
             time_fields = self._time_fmt_cache.get(table_id, {})
             
             if not time_fields:
                 return record
             
             # 复制记录以避免修改原始数据
             formatted_record = record.copy()
             fields = formatted_record.get('fields', {})
             
             # 遍历时间字段进行格式化
             for field_name, time_format in time_fields.items():
                 if field_name in fields:
                     field_value = fields[field_name]
                     
                     # 处理时间戳格式（毫秒）
                     if isinstance(field_value, (int, float)):
                         try:
                             from datetime import datetime
                             # 飞书时间戳通常是毫秒级
                             timestamp = field_value / 1000 if field_value > 1e10 else field_value
                             dt = datetime.fromtimestamp(timestamp)
                             
                             # 将飞书格式转换为Python格式
                             python_format = time_format.replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d').replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
                             formatted_time = dt.strftime(python_format)
                             fields[field_name] = formatted_time
                         except Exception as e:
                             print(f"格式化时间字段 {field_name} 失败: {e}")
                     
                     # 处理字符串格式的时间
                     elif isinstance(field_value, str) and field_value:
                         try:
                             from datetime import datetime
                             # 尝试解析常见的时间格式
                             for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y-%m-%d', '%Y/%m/%d']:
                                 try:
                                     dt = datetime.strptime(field_value, fmt)
                                     python_format = time_format.replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d').replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
                                     formatted_time = dt.strftime(python_format)
                                     fields[field_name] = formatted_time
                                     break
                                 except ValueError:
                                     continue
                         except Exception as e:
                             print(f"格式化时间字段 {field_name} 失败: {e}")
             
             return formatted_record
             
         except Exception as e:
             print(f"格式化记录时间失败: {e}")
             return record
    
    def update_cache(self) -> None:
        """
        更新缓存 cache_tables、cache_time_fmt
        """
        try:
            #print("开始更新缓存...")
            # 更新数据表缓存
            self._cache_tables()
            #print(f"数据表缓存更新完成，共缓存 {len(self._table_cache)} 个表")
            print(f'{len(self._table_cache)} 个表缓存完成：{self._table_cache}')
            # 更新时间格式缓存
            self._cache_time_fmt()
            time_field_count = sum(len(fields) for fields in self._time_fmt_cache.values())
            print(f"缓存 {time_field_count} 个时间字段：{self._time_fmt_cache}")
            
        except Exception as e:
            print(f"更新缓存失败: {e}")
    
    def _list_tables(self) -> Dict:
        """
        列出数据表
        
        Returns:
            数据表列表
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables"
        return self._make_request("GET", endpoint)
    
    def _list_fields(self, table_id: str) -> Dict:
        """
        列出数据表字段
        
        Args:
            table_id: 数据表ID
            
        Returns:
            字段列表
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields"
        return self._make_request("GET", endpoint)
    
    def list_records(self, table_id: str, params: Optional[Dict] = None) -> Dict:
        """
        列出所有记录
        
        Args:
            table_id: 数据表ID
            params: 查询参数
            
        Returns:
            记录列表
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        return self._make_request("GET", endpoint, params=params)
    
    def get_record(self, table_id: str, record_id: str) -> Dict:
        """
        根据记录ID查询记录详情
        
        Args:
            table_id: 数据表ID
            record_id: 记录ID
            
        Returns:
            记录详情
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        return self._make_request("GET", endpoint)
    
    def filter_records(self, table_id: str, filter_str: str) -> Dict:
        """
        过滤记录
        
        Args:
            table_id: 数据表ID
            filter_str: 过滤条件
            
        Returns:
            过滤后的记录
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        params = {"filter": filter_str}
        return self._make_request("GET", endpoint, params=params)
    
    def create_record(self, table_id: str, fields: Dict) -> Dict:
        """
        创建记录
        
        Args:
            table_id: 数据表ID
            fields: 字段数据
            
        Returns:
            创建结果
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        data = {"fields": fields}
        return self._make_request("POST", endpoint, data=data)
    
    def update_record(self, table_id: str, record_id: str, fields: Dict) -> Dict:
        """
        更新记录
        
        Args:
            table_id: 数据表ID
            record_id: 记录ID
            fields: 字段数据
            
        Returns:
            更新结果
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        data = {"fields": fields}
        return self._make_request("POST", endpoint, data=data)
    
    def delete_record(self, table_id: str, record_id: str) -> Dict:
        """
        删除记录
        
        Args:
            table_id: 数据表ID
            record_id: 记录ID
            
        Returns:
            删除结果
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        return self._make_request("POST", endpoint)
    
    def batch_create_records(self, table_id: str, records: List[Dict]) -> Dict:
        """
        批量创建记录
        
        Args:
            table_id: 数据表ID
            records: 记录列表
            
        Returns:
            创建结果
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch_create"
        data = {"records": records}
        return self._make_request("POST", endpoint, data=data)
    
    def batch_delete_records(self, table_id: str, record_ids: List[str]) -> Dict:
        """
        批量删除记录
        
        Args:
            table_id: 数据表ID
            record_ids: 记录ID列表
            
        Returns:
            删除结果
        """
        endpoint = f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch_delete"
        data = {"records": record_ids}
        return self._make_request("POST", endpoint, data=data)