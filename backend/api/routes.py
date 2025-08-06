"""
API路由定义
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request
from services.feishu_service import feishu_service
import logging

# 创建API蓝图
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_v1.route('/products', methods=['GET'])
def get_products():
    """
    获取产品列表（农户列表）
    
    Returns:
        JSON响应包含农户列表数据
    """
    try:
        logger.info("开始获取产品列表")
        
        # 从飞书获取农户列表
        result = feishu_service.get_farmer_list()
        
        if result['success']:
            logger.info(f"成功获取 {len(result['data']['farmers'])} 个产品")
            
            # 格式化响应数据
            products = []
            for farmer in result['data']['farmers']:
                product = {
                    'product_id': farmer['record_id'],
                    'product_name': farmer['farmer_name'],
                    'app_token': farmer['app_token'],
                    'auth_code': farmer['auth_code'],
                    'created_time': farmer['created_time'],
                    'last_modified_time': farmer['last_modified_time']
                }
                products.append(product)
            
            response_data = {
                'code': 0,
                'message': 'success',
                'data': {
                    'products': products,
                    'total': result['data']['total'],
                    'has_more': result['data']['has_more']
                }
            }
            
            return jsonify(response_data), 200
        else:
            logger.error(f"获取产品列表失败: {result['message']}")
            
            error_response = {
                'code': 1,
                'message': result['message'],
                'data': None
            }
            
            return jsonify(error_response), 500
            
    except Exception as e:
        logger.error(f"获取产品列表异常: {str(e)}")
        
        error_response = {
            'code': 1,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }
        
        return jsonify(error_response), 500

@api_v1.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    Returns:
        JSON响应表示服务状态
    """
    return jsonify({
        'code': 0,
        'message': 'API服务运行正常',
        'data': {
            'status': 'healthy',
            'version': '1.0.0'
        }
    }), 200
