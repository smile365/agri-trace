"""
配置文件加载模块
"""
import os
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
load_dotenv(find_dotenv(filename='.env'))

class Config:
    """应用配置类"""
    
    # 飞书API配置
    FEISHU_API_BASE_URL = os.environ.get('FEISHU_API_BASE_URL', 'https://base-api.feishu.cn')
    
    # 新增飞书多维表格配置
    PERSONAL_BASE_TOKEN = os.environ.get('PERSONAL_BASE_TOKEN')
    APP_TOKEN = os.environ.get('APP_TOKEN')
    
    # 多租户系统配置
    SYS_APP_TOKEN = os.environ.get('SYS_APP_TOKEN')
    SYS_PERSONAL_BASE_TOKEN = os.environ.get('SYS_PERSONAL_BASE_TOKEN')
    SYSTEM_TABLE_NAME = os.environ.get('SYSTEM_TABLE_NAME', '授权列表')
    
    # 缓存更新配置 分钟
    CACHE_UPDATE_INTERVAL = int(os.environ.get('CACHE_UPDATE_INTERVAL', 60))
    REDIS_DB_PATH = os.environ.get('REDIS_DB_PATH', 'cache.db')
    
    # Flask应用配置
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # 缓存配置
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 3000))
    
    # API限流配置
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    @classmethod
    def validate(cls):
        """验证必要的配置项是否存在"""
        required_configs = [
            'SYS_APP_TOKEN',
            'SYS_PERSONAL_BASE_TOKEN'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not getattr(cls, config):
                missing_configs.append(config)
        
        if missing_configs:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing_configs)}")
        
        return True

# 创建配置实例
config = Config()
