"""
API路由定义
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, Response
from services.feishu_service import feishu_service
from utils.dht11_processor import decode_dht11_message
import logging
import requests

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
            

            #logger.info(f"成功获取农户 {farmer_info['farmer_name']} 的完整信息")

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

            # 处理产品信息中的封面图和监控地址格式
            product_info = data.get('product_info', {}).copy()
            
            # 修改封面图格式
            if '封面图' in product_info and product_info['封面图']:
                if isinstance(product_info['封面图'], list) and len(product_info['封面图']) > 0:
                    file_token = product_info['封面图'][0].get('file_token', '')
                    if file_token:
                        product_info['封面图'] = f"http://127.0.0.1:5000/api/v1/img/{file_token}"
                    else:
                        product_info['封面图'] = ""
                else:
                    product_info['封面图'] = ""
            
            # 修改监控地址格式
            if '监控地址' in product_info and product_info['监控地址'] and isinstance(product_info['监控地址'], list) and len(product_info['监控地址']) > 0:
                    # 将 rtmp 协议改为 http，链接末尾增加 .flv
                    rtmp_url = product_info['监控地址'][0]['text']
                    # 提取 rtmp 地址中的流标识符
                    parts = rtmp_url.split('/')
                    if len(parts) > 3:
                        stream_id = parts[-1]
                        product_info['监控地址'] = f"http://srs.pxact.com/live/{stream_id}.flv"
                    else:
                        # 如果无法解析，使用默认地址
                        product_info['监控地址'] = "http://srs.pxact.com/live/recuu78lxajroy.flv"
            
            # 简化统计信息
            statistics = {}
            if data.get('statistics'):
                statistics = {
                    'feeding_count': data['statistics'].get('feeding_count', 0),
                    'process_count': data['statistics'].get('process_count', 0)
                }
            
            # 格式化响应数据
            response_data = {
                'code': 0,
                'message': 'success',
                'data': {
                    'product_info': product_info,
                    'feeding_records': feeding_records,
                    'breeding_process': breeding_process,
                    'statistics': statistics
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

@api_v1.route('/farm/table/fields', methods=['GET'])
def get_table_fields():
    """
    获取数据表的字段定义（Admin接口）

    Query Parameters:
        product_id: 产品ID（农户记录ID）
        tname: 数据表名称

    Returns:
        JSON响应包含数据表的字段定义
    """
    try:
        # 获取查询参数
        product_id = request.args.get('product_id')
        table_name = request.args.get('tname')

        logger.info(f"开始获取数据表字段定义，产品ID: {product_id}, 表名: {table_name}")

        # 验证必要参数
        if not product_id or len(product_id.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '缺少必要参数：product_id',
                'data': None
            }
            return jsonify(error_response), 400

        if not table_name or len(table_name.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '缺少必要参数：tname（数据表名称）',
                'data': None
            }
            return jsonify(error_response), 400

        # 从飞书获取数据表字段定义
        result = feishu_service.get_table_fields_by_name(product_id.strip(), table_name.strip())

        if result['success']:
            data = result['data']
            table_info = data['table_info']
            farmer_info = data['farmer_info']
            fields = data['fields']

            logger.info(f"成功获取农户 {farmer_info['farmer_name']} 的数据表 {table_info['table_name']} 的 {len(fields)} 个字段定义")

            # 格式化响应数据
            response_data = {
                'code': 0,
                'message': 'success',
                'data': {
                    'table_info': table_info,
                    'farmer_info': farmer_info,
                    'fields': fields,
                    'total': data['total'],
                    'has_more': data['has_more'],
                    'page_token': data.get('page_token')
                }
            }

            return jsonify(response_data), 200
        else:
            logger.error(f"获取数据表字段定义失败: {result['message']}")

            # 判断错误类型
            if 'RecordIdNotFound' in result['message'] or '404' in result['message']:
                error_response = {
                    'code': 1,
                    'message': '未找到指定的产品',
                    'data': None
                }
                return jsonify(error_response), 404
            elif '未找到名称为' in result['message']:
                error_response = {
                    'code': 1,
                    'message': result['message'],
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
        logger.error(f"获取数据表字段定义异常: {str(e)}")

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

@api_v1.route('/img/<file_token>', methods=['GET'])
def proxy_image(file_token):
    """
    图片代理接口

    Args:
        file_token: 飞书文件令牌

    Returns:
        图片数据流
    """
    try:
        logger.info(f"开始代理图片，文件令牌: {file_token}")

        # 构建飞书图片下载URL - 使用base-api域名
        feishu_url = f"https://base-api.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"

        # 使用FeishuService的认证头
        headers = feishu_service._get_headers()
        headers['User-Agent'] = 'Farm-Traceability-System/1.0'

        logger.info(f"使用认证头: Authorization: Bearer {feishu_service.personal_token[:20]}...")

        # 发起代理请求
        logger.info(f"向飞书请求图片: {feishu_url}")
        response = requests.get(feishu_url, headers=headers, stream=True, timeout=30)

        if response.status_code == 200:
            # 获取图片的Content-Type
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            content_length = response.headers.get('Content-Length')

            logger.info(f"成功获取图片，类型: {content_type}, 大小: {content_length}")

            # 创建响应对象，流式传输图片数据
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            # 设置响应头
            response_headers = {
                'Content-Type': content_type,
                'Cache-Control': 'public, max-age=3600',  # 缓存1小时
                'Access-Control-Allow-Origin': '*'  # 允许跨域
            }

            if content_length:
                response_headers['Content-Length'] = content_length

            return Response(generate(), headers=response_headers)

        else:
            logger.error(f"飞书图片下载失败，状态码: {response.status_code}, 响应: {response.text}")
            return jsonify({
                'code': 1,
                'message': f'图片下载失败，状态码: {response.status_code}',
                'data': None
            }), response.status_code

    except requests.exceptions.Timeout:
        logger.error(f"图片下载超时: {file_token}")
        return jsonify({
            'code': 1,
            'message': '图片下载超时',
            'data': None
        }), 504

    except requests.exceptions.RequestException as e:
        logger.error(f"图片下载网络错误: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'网络请求失败: {str(e)}',
            'data': None
        }), 500

    except Exception as e:
        logger.error(f"图片代理失败: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'图片代理失败: {str(e)}',
            'data': None
        }), 500



@api_v1.route('/dht/weather', methods=['GET'])
def baidu_verify():
    return 'e22c1b37c4260ac0fe1a2fae229f5eb1e99379d7286192e351d0e9aad29a5298'


@api_v1.route('/dht/weather', methods=['POST'])
def show_weather_info():
    """
    接受DHT11传感器数据并解码处理

    接收包含base64编码温湿度数据的JSON，解码后返回结构化的温湿度信息

    Returns:
        JSON响应包含解码后的DHT11传感器数据
    """
    try:
        data = request.get_json()
        humidity_temperature = decode_dht11_message(data)
        data['message'] = humidity_temperature
        logger.info(f"解码后的DHT11数据: {data}")
        return jsonify({
            'code': 200,
            'message': data['message'],
            'data': None
        }), 200
    except Exception as e:
        logger.error(f"DHT11数据解码失败: {str(e)}")
        return jsonify({
            'code': 1,
            'message': f'数据解码失败: {str(e)}',
            'data': None
        }), 400


