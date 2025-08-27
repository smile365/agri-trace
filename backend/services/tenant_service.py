"""多租户管理服务模块

负责多租户系统的初始化、租户数据管理和定时更新机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
import schedule
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from config import config
from services.cache_service import cache_service
from services.feishu_service import FeishuService

logger = logging.getLogger(__name__)

class TenantService:
    """多租户管理服务类"""
    
    def __init__(self):
        """初始化租户服务"""
        self.cache_service = cache_service
        self.tenant_nums = set()
        self.system_feishu_service = None
        self.tenat_feishu_service = {}
        self._update_thread = None
        self._stop_update = False
        
        # 系统管理表配置
        self.sys_app_token = getattr(config, 'SYS_APP_TOKEN', None)
        self.sys_personal_base_token = getattr(config, 'SYS_PERSONAL_BASE_TOKEN', None)
        self.system_table_name = getattr(config, 'SYSTEM_TABLE_NAME', '授权列表')
        
        # 缓存更新间隔（分钟）
        self.cache_update_interval = getattr(config, 'CACHE_UPDATE_INTERVAL', 5)
        
        logger.info("多租户管理服务初始化完成")
    
    def _init_system_feishu_service(self) -> bool:
        """初始化系统级飞书服务
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            if not self.sys_app_token or not self.sys_personal_base_token:
                logger.error("系统级飞书配置缺失: SYS_APP_TOKEN 或 SYS_PERSONAL_BASE_TOKEN")
                return False
            
            # 创建系统级飞书服务实例
            self.system_feishu_service= FeishuService(self.sys_app_token, self.sys_personal_base_token)
            
            logger.info("系统级飞书服务初始化成功")
            return True
        except Exception as e:
            logger.error(f"初始化系统级飞书服务失败: {str(e)}")
            return False
    
    def load_system_tenants(self) -> bool:
        """从系统管理表加载租户信息
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not self.system_feishu_service:
                if not self._init_system_feishu_service():
                    return False
            
            logger.debug("开始从系统管理表加载租户信息")
            
            # 获取系统管理表数据
            result = self.system_feishu_service.get_table_records(self.system_table_name)
            
            if not result['success']:
                logger.error(f"获取系统管理表数据失败: {result['message']}")
                return False
            
            records = result['data'].get('items', [])
            if not records:
                logger.warning("系统管理表中没有租户数据")
                return True
            
            tenant_count = 0
            for record in records:
                fields = record.get('fields', {})
                
                # 提取租户信息
                tenant_num = fields.get('编号')
                tenant_name = fields.get('租户名称')
                app_token = fields.get('APP_TOKEN')
                personal_base_token = fields.get('PERSONAL_BASE_TOKEN')
                authorized_count = fields.get('授权农户数量', 0)
                tenant_id = record.get('record_id')
                
                # 验证必要字段
                if not all([tenant_num, app_token, personal_base_token]):
                    logger.warning(f"租户数据不完整，跳过: 编号={tenant_num}, 名称={tenant_name}")
                    #print(record)
                    continue
                
                self.tenant_nums.add(tenant_num)
                
                # 构建租户数据
                tenant_data = {
                    'tenant_num': tenant_num,
                    'tenant_name': tenant_name,
                    'app_token': app_token,
                    'personal_base_token': personal_base_token,
                    'authorized_count': int(authorized_count) if authorized_count else 0,
                    'tenant_id': tenant_id,
                    'loaded_at': datetime.now().isoformat()
                }
                
                # 缓存租户信息
                if self.cache_service.cache_tenant_info(tenant_num, tenant_data):
                    tenant_count += 1
                    logger.debug(f"成功加载租户: {tenant_name} ({tenant_num})")
                else:
                    logger.error(f"缓存租户信息失败,编号: {tenant_num}")
            
            logger.info(f"成功加载 {tenant_count} 个租户信息")
            return tenant_count > 0
            
        except Exception as e:
            logger.error(f"加载系统租户信息失败: {str(e)}")
            return False
    
    def load_tenant_tables(self, tenant_num: str) -> bool:
        """加载指定租户的表信息
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 创建租户专用的飞书服务
            tenant_info = self.cache_service.get_tenant_info(tenant_num)
            tenant_feishu = FeishuService(tenant_info['app_token'], tenant_info['personal_base_token'])
            self.tenat_feishu_service[tenant_num] = tenant_feishu
            logger.info(f"成功加载租户表信息: {tenant_num}, 表数量: {len(tenant_feishu.tables_cache)}")
            return len(tenant_feishu.tables_cache) > 0
        except Exception as e:
            logger.error(f"加载租户表信息失败 {tenant_num}: {str(e)}")
            return False
    
    def get_tenant_feishu_service(self, tenant_num: str) -> FeishuService:
        tenant_feishu = self.tenat_feishu_service[str(tenant_num)]
        if not tenant_feishu:
            logger.error(f"未找到租户飞书服务: {tenant_num}")
            return None
        return tenant_feishu
    

    def load_tenant_farmer_ids(self, tenant_num: str) -> bool:
        """加载指定租户的农户ID列表
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            bool: 加载是否成功
        """
        try:

            # 获取租户表信息
            tenant_feishu = self.get_tenant_feishu_service(tenant_num)
            
            farmer_data = tenant_feishu.get_table_records('农户管理')
            if not farmer_data['success']:
                logger.error(f"获取农户管理表数据失败: {farmer_data['message']}")
                return False
            # 获取农户数据
            records = farmer_data['data'].get('items', [])
            farmer_ids = [record.get('record_id') for record in records if record.get('record_id')]
            # 缓存农户ID列表
            tenant_info = self.cache_service.get_tenant_info(tenant_num)
            authorized_count = tenant_info.get('authorized_count', 0)
            if self.cache_service.cache_farmer_ids(tenant_num, farmer_ids, authorized_count):
                logger.info(f"租户：{tenant_num} , 授权: {len(farmer_ids)}、{authorized_count}")
                return True
            else:
                logger.error(f"缓存农户ID列表失败: {tenant_num}")
                return False
                
        except Exception as e:
            logger.error(f"加载农户ID列表失败 {tenant_num}: {str(e)}")
            return False
    
    def initialize_cache(self) -> bool:
        """初始化所有缓存数据
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            #logger.info("开始初始化多租户缓存数据")
            
            # 1. 加载系统租户信息
            if not self.load_system_tenants():
                logger.error("加载系统租户信息失败")
                return False
            
            # 3. 为每个租户加载表信息和农户ID
            success_count = 0
            for tenant_num in self.tenant_nums:
                try:
                    # 加载表信息
                    logger.info(f"开始加载租户表信息: {tenant_num}")
                    if self.load_tenant_tables(tenant_num):
                        # 加载农户ID列表
                        if self.load_tenant_farmer_ids(tenant_num):
                            success_count += 1
                        else:
                            logger.warning(f"加载农户ID失败: {tenant_num}")
                    else:
                        logger.warning(f"加载表信息失败: {tenant_num}")
                except Exception as e:
                    logger.error(f"处理租户失败 {tenant_num}: {str(e)}")
            
            logger.info(f"缓存初始化完成，成功处理 {success_count} 个租户")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"初始化缓存失败: {str(e)}")
            return False
    
    def update_cache(self) -> bool:
        """更新缓存数据
        
        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info("开始更新缓存数据")
            return self.initialize_cache()
        except Exception as e:
            logger.error(f"更新缓存失败: {str(e)}")
            return False
    
    def start_cache_update_scheduler(self):
        """启动缓存更新调度器"""
        try:
            # 设置定时任务
            schedule.every(self.cache_update_interval).minutes.do(self.update_cache)
            
            def run_scheduler():
                while not self._stop_update:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次
            
            # 启动后台线程
            self._update_thread = threading.Thread(target=run_scheduler, daemon=True)
            self._update_thread.start()
            
            logger.info(f"缓存更新调度器已启动，更新间隔: {self.cache_update_interval} 分钟")
        except Exception as e:
            logger.error(f"启动缓存更新调度器失败: {str(e)}")
    
    def stop_cache_update_scheduler(self):
        """停止缓存更新调度器"""
        try:
            self._stop_update = True
            if self._update_thread and self._update_thread.is_alive():
                self._update_thread.join(timeout=5)
            logger.info("缓存更新调度器已停止")
        except Exception as e:
            logger.error(f"停止缓存更新调度器失败: {str(e)}")
    
    def validate_tenant_access(self, tenant_num: str, farmer_id: str) -> Dict[str, Any]:
        """验证租户访问权限
        
        Args:
            tenant_num: 租户编号
            farmer_id: 农户ID
            
        Returns:
            Dict: 验证结果，包含success、message、tenant_info等
        """
        try:
            # 检查租户是否存在
            tenant_info = self.cache_service.get_tenant_info(tenant_num)
            if not tenant_info:
                return {
                    'success': False,
                    'message': f'租户不存在: {tenant_num}',
                    'tenant_info': None
                }
            
            # 检查农户ID是否在授权列表中
            if not self.cache_service.is_farmer_authorized(tenant_num, farmer_id):
                return {
                    'success': False,
                    'message': '农户记录不存在或授权农户数量已超限额',
                    'tenant_info': tenant_info
                }
            
            return {
                'success': True,
                'message': '验证通过',
                'tenant_info': tenant_info
            }
            
        except Exception as e:
            logger.error(f"验证租户访问权限失败: {str(e)}")
            return {
                'success': False,
                'message': f'验证失败: {str(e)}',
                'tenant_info': None
            }
    
    def get_tenant_info(self, tenant_num: str) -> Optional[Dict[str, Any]]:
        """获取租户信息
        
        Args:
            tenant_num: 租户编号
            
        Returns:
            Optional[Dict]: 租户信息，如果不存在返回None
        """
        return self.cache_service.get_tenant_info(tenant_num)
    
    def validate_farmer_access(self, tenant_num: str, farmer_id: str) -> bool:
        """验证农户访问权限
        
        Args:
            tenant_num: 租户编号
            farmer_id: 农户ID
            
        Returns:
            bool: 是否有访问权限
        """
        return self.cache_service.is_farmer_authorized(tenant_num, farmer_id)
    
    def get_tenant_farm_info(self, tenant_num: str, farmer_id: str) -> Dict[str, Any]:
        """获取租户专用的农户完整信息
        
        Args:
            tenant_num: 租户编号
            farmer_id: 农户ID
            
        Returns:
            Dict: 包含success、data、message的响应
        """
        try:
            # 获取租户信息
            tenant_info = self.cache_service.get_tenant_info(tenant_num)
            if not tenant_info:
                return {
                    'success': False,
                    'message': f'租户不存在: {tenant_num}',
                    'data': None
                }
            
            # 创建租户专用的飞书服务
            tenant_feishu = self.get_tenant_feishu_service(tenant_num)
            # 调用飞书服务获取农户完整信息
            result = tenant_feishu.get_farm_complete_info(farmer_id)
            return result
            
        except Exception as e:
            logger.error(f"获取租户农户信息异常 {tenant_num}/{farmer_id}: {str(e)}")
            return {
                'success': False,
                'message': f'获取农户信息失败: {str(e)}',
                'data': None
            }
    
    def get_tenant_stats(self) -> Dict[str, Any]:
        """获取租户统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            tenant_numbers = self.tenant_nums
            stats = {
                'total_tenants': len(tenant_numbers),
                'tenants': []
            }
            
            for tenant_num in tenant_numbers:
                tenant_info = self.cache_service.get_tenant_info(tenant_num)
                farmer_data = self.cache_service.get_farmer_ids(tenant_num)
                
                tenant_stat = {
                    'tenant_num': tenant_num,
                    'tenant_name': tenant_info.get('tenant_name', 'N/A') if tenant_info else 'N/A',
                    'authorized_count': tenant_info.get('authorized_count', 0) if tenant_info else 0,
                    'farmer_count': len(farmer_data.get('farmer_ids', [])) if farmer_data else 0
                }
                stats['tenants'].append(tenant_stat)
            
            return stats
        except Exception as e:
            logger.error(f"获取租户统计信息失败: {str(e)}")
            return {'total_tenants': 0, 'tenants': []}

# 全局租户服务实例
tenant_service = TenantService()