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

@api_v1.route('/product/<string:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """
    获取单个产品详情

    Args:
        product_id: 产品ID（农户记录ID）

    Returns:
        JSON响应包含产品详情数据
    """
    try:
        logger.info(f"开始获取产品详情，产品ID: {product_id}")

        # 验证产品ID格式
        if not product_id or len(product_id.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '产品ID不能为空',
                'data': None
            }
            return jsonify(error_response), 400

        # 从飞书获取农户详情
        result = feishu_service.get_farmer_by_id(product_id.strip())

        if result['success']:
            farmer_data = result['data']

            # 检查是否找到记录
            if not farmer_data or not farmer_data.get('record_id'):
                error_response = {
                    'code': 1,
                    'message': '未找到指定的产品',
                    'data': None
                }
                return jsonify(error_response), 404

            logger.info(f"成功获取产品详情: {farmer_data.get('farmer_name', '未知')}")

            # 格式化响应数据
            product_detail = {
                'product_id': farmer_data['record_id'],
                'product_name': farmer_data['farmer_name'],
                'app_token': farmer_data['app_token'],
                'auth_code': farmer_data['auth_code'],
                'contact': farmer_data.get('contact', ''),
                'address': farmer_data.get('address', ''),
                'created_time': farmer_data['created_time'],
                'last_modified_time': farmer_data['last_modified_time'],
                'created_by': farmer_data.get('created_by'),
                'last_modified_by': farmer_data.get('last_modified_by')
            }

            response_data = {
                'code': 0,
                'message': 'success',
                'data': product_detail
            }

            return jsonify(response_data), 200
        else:
            logger.error(f"获取产品详情失败: {result['message']}")

            # 判断是否为404错误
            if '404' in result['message'] or 'not found' in result['message'].lower():
                error_response = {
                    'code': 1,
                    'message': '未找到指定的产品',
                    'data': None
                }
                return jsonify(error_response), 404
            else:
                error_response = {
                    'code': 1,
                    'message': result['message'],
                    'data': None
                }
                return jsonify(error_response), 500

    except Exception as e:
        logger.error(f"获取产品详情异常: {str(e)}")

        error_response = {
            'code': 1,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }

        return jsonify(error_response), 500

@api_v1.route('/farm/tables', methods=['GET'])
def get_farm_tables():
    """
    获取农户的数据表列表

    Query Parameters:
        product_id: 产品ID（农户记录ID）

    Returns:
        JSON响应包含农户的数据表列表
    """
    try:
        # 获取查询参数
        product_id = request.args.get('product_id')

        logger.info(f"开始获取农户数据表列表，产品ID: {product_id}")

        # 验证产品ID参数
        if not product_id or len(product_id.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '缺少必要参数：product_id',
                'data': None
            }
            return jsonify(error_response), 400

        # 从飞书获取农户数据表列表
        result = feishu_service.get_farmer_tables(product_id.strip())

        if result['success']:
            data = result['data']
            farmer_info = data['farmer_info']
            tables = data['tables']

            logger.info(f"成功获取农户 {farmer_info['farmer_name']} 的 {len(tables)} 个数据表")

            # 格式化响应数据
            response_data = {
                'code': 0,
                'message': 'success',
                'data': {
                    'farmer_info': {
                        'product_id': farmer_info['product_id'],
                        'farmer_name': farmer_info['farmer_name'],
                        'app_token': farmer_info['app_token']
                        # 注意：出于安全考虑，不在响应中返回完整的授权码
                    },
                    'tables': tables,
                    'total': data['total'],
                    'has_more': data['has_more'],
                    'page_token': data.get('page_token')
                }
            }

            return jsonify(response_data), 200
        else:
            logger.error(f"获取农户数据表列表失败: {result['message']}")

            # 判断错误类型
            if 'RecordIdNotFound' in result['message'] or '404' in result['message']:
                error_response = {
                    'code': 1,
                    'message': '未找到指定的产品',
                    'data': None
                }
                return jsonify(error_response), 404
            elif '缺少必要的API配置信息' in result['message']:
                error_response = {
                    'code': 1,
                    'message': result['message'],
                    'data': None
                }
                return jsonify(error_response), 400
            else:
                error_response = {
                    'code': 1,
                    'message': result['message'],
                    'data': None
                }
                return jsonify(error_response), 500

    except Exception as e:
        logger.error(f"获取农户数据表列表异常: {str(e)}")

        error_response = {
            'code': 1,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }

        return jsonify(error_response), 500

@api_v1.route('/farm/info', methods=['GET'])
def get_farm_info():
    """
    获取农户完整信息（用于静态页面展示）

    Query Parameters:
        product_id: 产品ID（农户记录ID）

    Returns:
        JSON响应包含农户的完整信息，包括商品信息、饲喂记录、养殖流程等
    """
    try:
        # 获取查询参数
        product_id = request.args.get('product_id')

        logger.info(f"开始获取农户完整信息，产品ID: {product_id}")

        # 验证产品ID参数
        if not product_id or len(product_id.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '缺少必要参数：product_id',
                'data': None
            }
            return jsonify(error_response), 400

        # 从飞书获取农户完整信息
        result = feishu_service.get_farm_complete_info(product_id.strip())

        if result['success']:
            data = result['data']
            farmer_info = data['farmer_info']

            logger.info(f"成功获取农户 {farmer_info['farmer_name']} 的完整信息")

            # 格式化时间戳
            def format_timestamp(timestamp):
                if timestamp and isinstance(timestamp, (int, float)):
                    from datetime import datetime
                    try:
                        dt = datetime.fromtimestamp(timestamp / 1000)  # 飞书时间戳是毫秒
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        return None
                return None

            # 处理饲喂记录时间格式
            feeding_records = []
            for record in data.get('feeding_records', []):
                formatted_record = record.copy()
                formatted_record['operation_time_formatted'] = format_timestamp(record.get('operation_time'))
                formatted_record['created_time_formatted'] = format_timestamp(record.get('created_time'))
                feeding_records.append(formatted_record)

            # 处理养殖流程时间格式
            breeding_process = []
            for record in data.get('breeding_process', []):
                formatted_record = record.copy()
                formatted_record['operation_time_formatted'] = format_timestamp(record.get('operation_time'))
                formatted_record['created_time_formatted'] = format_timestamp(record.get('created_time'))
                breeding_process.append(formatted_record)

            # 格式化响应数据
            response_data = {
                'code': 0,
                'message': 'success',
                'data': {
                    'farmer_info': {
                        'product_id': farmer_info['product_id'],
                        'farmer_name': farmer_info['farmer_name'],
                        'app_token': farmer_info['app_token']
                        # 注意：出于安全考虑，不在响应中返回完整的授权码
                    },
                    'product_info': data.get('product_info', {}),
                    'feeding_records': feeding_records,
                    'breeding_process': breeding_process,
                    'statistics': data.get('statistics', {})
                }
            }

            return jsonify(response_data), 200
        else:
            logger.error(f"获取农户完整信息失败: {result['message']}")

            # 判断错误类型
            if 'RecordIdNotFound' in result['message'] or '404' in result['message']:
                error_response = {
                    'code': 1,
                    'message': '未找到指定的产品',
                    'data': None
                }
                return jsonify(error_response), 404
            elif '缺少必要的API配置信息' in result['message']:
                error_response = {
                    'code': 1,
                    'message': result['message'],
                    'data': None
                }
                return jsonify(error_response), 400
            else:
                error_response = {
                    'code': 1,
                    'message': result['message'],
                    'data': None
                }
                return jsonify(error_response), 500

    except Exception as e:
        logger.error(f"获取农户完整信息异常: {str(e)}")

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
