"""
Flask应用主文件
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging
from config import config
from api.routes import api_v1
from services.tenant_service import tenant_service

def create_app():
    """创建Flask应用"""
    # 设置模板和静态文件路径
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # 配置应用
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.FLASK_DEBUG
    
    # 启用CORS
    CORS(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    app.register_blueprint(api_v1)
    
    # 初始化多租户系统
    init_multi_tenant_system(app)

    # 前端页面路由
    @app.route('/<path:filename>.html')
    def html_page(filename):
        return render_template(f'{filename}.html')


    # 静态文件路由
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
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

def init_multi_tenant_system(app):
    """初始化多租户系统"""
    try:
        #print("正在初始化多租户系统...")
        
        # 初始化缓存数据
        if tenant_service.initialize_cache():
            #print("✓ 多租户缓存初始化成功")
            
            # 启动缓存更新调度器
            tenant_service.start_cache_update_scheduler()
            #print("✓ 缓存更新调度器启动成功")
            
            # 获取统计信息
            stats = tenant_service.get_tenant_stats()
            print(f"✓ 多租户系统就绪，共加载 {stats['total_tenants']} 个租户")
        else:
            print("⚠ 多租户缓存初始化失败，系统将以单租户模式运行")
            
    except Exception as e:
        print(f"⚠ 多租户系统初始化异常: {str(e)}")
        print("系统将以单租户模式运行")

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
