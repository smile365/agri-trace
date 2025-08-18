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
    MASTER_APP_TOKEN = os.environ.get('MASTER_APP_TOKEN')
    MASTER_PERSONAL_BASE_TOKEN = os.environ.get('MASTER_PERSONAL_BASE_TOKEN')
    MASTER_TABLE_ID = os.environ.get('MASTER_TABLE_ID')
    
    # 新增飞书多维表格配置
    PERSONAL_BASE_TOKEN = os.environ.get('PERSONAL_BASE_TOKEN')
    APP_TOKEN = os.environ.get('APP_TOKEN')
    
    # Flask应用配置
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # 缓存配置
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    # API限流配置
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    @classmethod
    def validate(cls):
        """验证必要的配置项是否存在"""
        required_configs = [
            'MASTER_APP_TOKEN',
            'MASTER_PERSONAL_BASE_TOKEN', 
            'MASTER_TABLE_ID',
            'PERSONAL_BASE_TOKEN',
            'APP_TOKEN'
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
