"""
Flask应用主文件
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
import logging
from config import config
from api.routes import api_v1

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置应用
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.FLASK_DEBUG
    
    # 启用CORS
    CORS(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    app.register_blueprint(api_v1)
    
    # 根路径
    @app.route('/')
    def index():
        return jsonify({
            'message': '农产品溯源系统API',
            'version': '1.0.0',
            'endpoints': {
                'products': '/api/v1/products',
                'product_detail': '/api/v1/product/{id}',
                'farm_tables': '/api/v1/farm/tables?product_id={id}',
                'farm_info': '/api/v1/farm/info?product_id={id}',
                'table_fields': '/api/v1/farm/table/fields?product_id={id}&tname={table_name}',
                'health': '/api/v1/health'
            }
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': '接口不存在',
            'data': None
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500
    
    return app

def setup_logging(app):
    """设置日志配置"""
    if not app.debug:
        # 创建日志目录
        log_dir = os.path.dirname(config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置文件日志
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        app.logger.info('农产品溯源系统启动')

if __name__ == '__main__':
    try:
        # 验证配置
        config.validate()
        print("✓ 配置验证通过")
        
        # 创建应用
        app = create_app()
        
        print(f"启动Flask应用...")
        print(f"访问地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
        print(f"API文档: http://{config.FLASK_HOST}:{config.FLASK_PORT}/api/v1/products")
        
        # 启动应用
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
        
    except Exception as e:
        print(f"✗ 启动失败: {str(e)}")
        exit(1)
