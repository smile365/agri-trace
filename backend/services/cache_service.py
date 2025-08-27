"""多租户缓存服务模块

实现基于redislite的多租户数据缓存管理，包括：
- 租户授权信息缓存
- 租户表数据缓存  
- 农户ID列表缓存
- 缓存更新机制
"""

import os
import json
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redislite
import logging

logger = logging.getLogger(__name__)

class MultiTenantCacheService:
    """多租户缓存服务类"""
    
    def __init__(self, db_path: str = None):
        """初始化缓存服务
        
        Args:
            db_path: Redis数据库文件路径，默认为项目根目录下的cache.db
        """
        if db_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(project_root, 'cache.db')
            
        self.redis_client = redislite.Redis(db_path)
        self._lock = threading.Lock()
        
        # 缓存键前缀
        self.TENANT_PREFIX = "tenant:"
        self.TENANT_TABLES_PREFIX = "tenant_tables:"
        self.FARMER_IDS_PREFIX = "farmer_ids:"
        self.SYSTEM_PREFIX = "system:"
        
        logger.info(f"多租户缓存服务初始化完成，数据库路径: {db_path}")
    
    def _get_tenant_key(self, tenant_num: str) -> str:
        """获取租户信息缓存键"""
        return f"{self.TENANT_PREFIX}{tenant_num}"
    
    def _get_tenant_tables_key(self, tenant_num: str) -> str:
        """获取租户表信息缓存键"""
        return f"{self.TENANT_TABLES_PREFIX}{tenant_num}"
    
    def _get_farmer_ids_key(self, tenant_num: str) -> str:
        """获取农户ID列表缓存键"""
        return f"{self.FARMER_IDS_PREFIX}{tenant_num}"
    
    def cache_tenant_info(self, tenant_num: str, tenant_data: Dict[str, Any]) -> bool:
        """缓存租户授权信息
        
        Args:
            tenant_num: 租户编号
            tenant_data: 租户数据，包含租户名称、APP_TOKEN、PERSONAL_BASE_TOKEN等
            
        Returns:
            bool: 缓存是否成功
        """
        try:
            with self._lock:
                key = self._get_tenant_key(tenant_num)
                # 添加缓存时间戳
                tenant_data['cached_at'] = datetime.now().isoformat()
                value = json.dumps(tenant_data, ensure_ascii=False)
                self.redis_client.set(key, value)
                logger.debug(f"成功缓存租户信息: {tenant_num}")
                return True
        except Exception as e:
            logger.error(f"缓存租户信息失败 {tenant_num}: {str(e)}")
            return False
    
    def get_tenant_info(self, tenant_num: str) -> Optional[Dict[str, Any]]:
        """获取租户授权信息
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            Dict: 租户信息，如果不存在返回None
        """
        try:
            key = self._get_tenant_key(tenant_num)
            value = self.redis_client.get(key)
            if value:
                return json.loads(value.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"获取租户信息失败 {tenant_num}: {str(e)}")
            return None
    
    def cache_tenant_tables(self, tenant_num: str, tables_data: List[Dict[str, str]]) -> bool:
        """缓存租户表信息
        
        Args:
            tenant_num: 租户编号
            tables_data: 表数据列表，每个元素包含table_name和table_id
            
        Returns:
            bool: 缓存是否成功
        """
        try:
            with self._lock:
                key = self._get_tenant_tables_key(tenant_num)
                cache_data = {
                    'tables': tables_data,
                    'cached_at': datetime.now().isoformat()
                }
                value = json.dumps(cache_data, ensure_ascii=False)
                self.redis_client.set(key, value)
                logger.debug(f"成功缓存租户表信息: {tenant_num}, 表数量: {len(tables_data)}")
                return True
        except Exception as e:
            logger.error(f"缓存租户表信息失败 {tenant_num}: {str(e)}")
            return False
    
    def get_tenant_tables(self, tenant_num: str) -> Optional[List[Dict[str, str]]]:
        """获取租户表信息
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            List: 表信息列表，如果不存在返回None
        """
        try:
            key = self._get_tenant_tables_key(tenant_num)
            value = self.redis_client.get(key)
            if value:
                cache_data = json.loads(value.decode('utf-8'))
                return cache_data.get('tables', [])
            return None
        except Exception as e:
            logger.error(f"获取租户表信息失败 {tenant_num}: {str(e)}")
            return None
    
    def cache_farmer_ids(self, tenant_num: str, farmer_ids: List[str], authorized_count: int) -> bool:
        """缓存农户ID列表
        
        Args:
            tenant_num: 租户编号
            farmer_ids: 农户ID列表
            authorized_count: 授权农户数量
            
        Returns:
            bool: 缓存是否成功
        """
        try:
            with self._lock:
                key = self._get_farmer_ids_key(tenant_num)
                # 只缓存授权数量内的农户ID
                authorized_ids = farmer_ids[:authorized_count]
                cache_data = {
                    'farmer_ids': authorized_ids,
                    'authorized_count': authorized_count,
                    'total_count': len(farmer_ids),
                    'cached_at': datetime.now().isoformat()
                }
                value = json.dumps(cache_data, ensure_ascii=False)
                self.redis_client.set(key, value)
                logger.info(f"成功缓存农户ID列表: {tenant_num}, 授权数量: {len(authorized_ids)}/{len(farmer_ids)}")
                return True
        except Exception as e:
            logger.error(f"缓存农户ID列表失败 {tenant_num}: {str(e)}")
            return False
    
    def get_farmer_ids(self, tenant_num: str) -> Optional[Dict[str, Any]]:
        """获取农户ID列表
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            Dict: 包含farmer_ids、authorized_count等信息，如果不存在返回None
        """
        try:
            key = self._get_farmer_ids_key(tenant_num)
            value = self.redis_client.get(key)
            if value:
                return json.loads(value.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"获取农户ID列表失败 {tenant_num}: {str(e)}")
            return None
    
    def is_farmer_authorized(self, tenant_num: str, farmer_id: str) -> bool:
        """检查农户ID是否在授权列表中
        
        Args:
            tenant_num: 租户编号
            farmer_id: 农户ID
            
        Returns:
            bool: 是否授权
        """
        farmer_data = self.get_farmer_ids(tenant_num)
        if farmer_data:
            return farmer_id in farmer_data.get('farmer_ids', [])
        return False
    
    def get_all_tenant_numbers(self) -> List[str]:
        """获取所有租户编号
        
        Returns:
            List: 租户编号列表
        """
        try:
            pattern = f"{self.TENANT_PREFIX}*"
            keys = self.redis_client.keys(pattern)
            tenant_numbers = []
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                tenant_num = key_str.replace(self.TENANT_PREFIX, '')
                tenant_numbers.append(tenant_num)
            return tenant_numbers
        except Exception as e:
            logger.error(f"获取租户编号列表失败: {str(e)}")
            return []
    
    def clear_tenant_cache(self, tenant_num: str) -> bool:
        """清除指定租户的所有缓存
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            bool: 清除是否成功
        """
        try:
            with self._lock:
                keys_to_delete = [
                    self._get_tenant_key(tenant_num),
                    self._get_tenant_tables_key(tenant_num),
                    self._get_farmer_ids_key(tenant_num)
                ]
                
                deleted_count = 0
                for key in keys_to_delete:
                    if self.redis_client.delete(key):
                        deleted_count += 1
                
                logger.info(f"清除租户缓存: {tenant_num}, 删除键数量: {deleted_count}")
                return deleted_count > 0
        except Exception as e:
            logger.error(f"清除租户缓存失败 {tenant_num}: {str(e)}")
            return False
    
    def clear_all_cache(self) -> bool:
        """清除所有缓存
        
        Returns:
            bool: 清除是否成功
        """
        try:
            with self._lock:
                self.redis_client.flushall()
                logger.info("成功清除所有缓存")
                return True
        except Exception as e:
            logger.error(f"清除所有缓存失败: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            Dict: 缓存统计信息
        """
        try:
            tenant_count = len(self.get_all_tenant_numbers())
            
            # 获取数据库信息
            info = self.redis_client.info()
            
            stats = {
                'tenant_count': tenant_count,
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_usage': info.get('used_memory_human', 'N/A'),
                'uptime': info.get('uptime_in_seconds', 0)
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭缓存连接"""
        try:
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
                logger.info("缓存连接已关闭")
        except Exception as e:
            logger.error(f"关闭缓存连接失败: {str(e)}")

# 全局缓存服务实例
cache_service = MultiTenantCacheService()