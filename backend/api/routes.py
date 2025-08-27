"""
API路由定义
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, Response
from services.tenant_service import tenant_service
from utils.lot_decode import decode_dht11_message,decode_nt1b_message
import logging
import requests
from config import config
from urllib.parse import parse_qs, urlparse
# 创建API蓝图
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_v1.route('/live/callback', methods=['POST'])
def live_callback():
    """
    直播回调接口
    POST /live/callback HTTP/1.1
    Content-Type: application/json
    Body:
        { 'param': '?id=recuU78lxajRoy&num=1', 'stream': 'u78lxajroy'}
    """
    data = request.json
    logger.info(f'live_callback request data: {data}')
    if not data:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    if data.get('action') != 'on_publish':
        return jsonify({'code': 0, 'msg': 'ok'}), 200
    param = data.get('param')
    if not param:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    # 从param中提取 product_id 和 tenant_num
    # param格式: '?id=recuU78lxajRoy&num=1'
    try:
        parsed = urlparse(param)
        query_params = parse_qs(parsed.query)
        
        product_id = query_params.get('id', [None])[0]
        tenant_num = query_params.get('num', [None])[0]
        
        if not product_id or not tenant_num:
            return jsonify({'code': 400, 'msg': '参数格式错误，缺少id或num'}), 400
            
        # 转换tenant_num为整数
        tenant_num = int(tenant_num)
        
    except (ValueError, TypeError) as e:
        return jsonify({'code': 400, 'msg': '参数格式错误'}), 400
    
    if not tenant_service.validate_farmer_access(tenant_num, product_id.strip()):
        return jsonify({'code': 403, 'msg': '无权限'}), 403
    return jsonify({'code': 0, 'msg': 'ok'})


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
        tenant_num = request.args.get('tenant_num') or 1

        logger.debug(f"开始获取农户完整信息，产品ID: {product_id}, 租户编号: {tenant_num}")

        # 验证产品ID参数
        if not product_id or len(product_id.strip()) == 0:
            error_response = {
                'code': 1,
                'message': '缺少必要参数：product_id',
                'data': None
            }
            return jsonify(error_response), 400
        
        # 验证租户编号是否有效
        tenant_info = tenant_service.get_tenant_info(tenant_num)
        if not tenant_info:
            error_response = {
                'code': 1,
                'message': '无效的租户编号',
                'data': None
            }
            return jsonify(error_response), 403
        
        # 验证农户ID是否在该租户的授权列表中
        if not tenant_service.validate_farmer_access(tenant_num, product_id.strip()):
            error_response = {
                'code': 1,
                'message': '此记录不存在或授权农户数量已超限额',
                'data': None
            }
            return jsonify(error_response), 403
        
        # 使用租户专用的飞书服务获取数据
        result = tenant_service.get_tenant_farm_info(tenant_num, product_id.strip())


        # 数据获取逻辑已在上面的多租户验证中处理

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
                
                # 处理 images 字段格式
                if 'images' in formatted_record and formatted_record['images']:
                    if isinstance(formatted_record['images'], list):
                        processed_images = []
                        for img in formatted_record['images']:
                            if isinstance(img, dict) and 'file_token' in img:
                                file_token = img['file_token']
                                if file_token:
                                    processed_images.append(f"/api/v1/img/{file_token}")
                        formatted_record['images'] = processed_images
                
                breeding_process.append(formatted_record)

            # 处理产品信息中的封面图和监控地址格式
            product_info = data.get('product_info', {}).copy()
            
            # 修改封面图格式
            if '封面图' in product_info and product_info['封面图']:
                if isinstance(product_info['封面图'], list) and len(product_info['封面图']) > 0:
                    file_token = product_info['封面图'][0].get('file_token', '')
                    if file_token:
                        product_info['封面图'] = f"/api/v1/img/{file_token}?num={tenant_num}"
                    else:
                        product_info['封面图'] = ""
                else:
                    product_info['封面图'] = ""
            
            # 修改监控地址格式
            if '监控地址' in product_info and product_info['监控地址'] and isinstance(product_info['监控地址'], list) and len(product_info['监控地址']) > 0:
                    # 将 rtmp 协议改为 http，链接末尾增加 .flv
                    rtmp_url = product_info['监控地址'][0]['text']
                    logger.info(f"原始监控地址: {rtmp_url}")
                    # 提取 rtmp 地址中的流标识符
                    parts = rtmp_url.split('?')[0].split('/')
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
                    'sensor': data.get('sensor', {}),
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
        logger.debug(f"开始代理图片，文件令牌: {file_token}")
        # 获取查询参数
        tenant_num = request.args.get('num') or '1'
        # 构建飞书图片下载URL - 使用base-api域名
        feishu_url = f"{config.FEISHU_API_BASE_URL}/open-apis/drive/v1/medias/{file_token}/download"

        # 使用FeishuService的认证头
        headers = tenant_service.get_tenant_feishu_service(tenant_num)._get_headers()
        # 发起代理请求
        logger.debug(f"向飞书请求图片: {feishu_url}")
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

@api_v1.route('/test/devices', methods=['GET', 'POST'])
def show_test_devices():
    # 打印请求参数 & 请求体等
    # print(f'请求方法: {request.method}')
    # print(f'URL参数: {request.args}')
    # print(f'请求头: {dict(request.headers)}')
    # print(f'完整URL: {request.url}')
    # print(f'查询字符串: {request.query_string.decode()}')
    
    # 如果是POST请求，打印请求体
    if request.method == 'POST':
        #print(f'Content-Type: {request.content_type}')
        if request.is_json:
            original_data = decode_nt1b_message(request.get_json())
            sensor_data = original_data['sensor_data']
            print(f"传感器数据: {sensor_data}")
        elif request.form:
            print(f'表单数据: {request.form}')
        else:
            print(f'原始数据: {request.get_data().decode()}')
    
    return 'c05b4392ea4b5d4cd1464ef83be1dba00f30f662c17dc453c96a5794594191a0'

@api_v1.route('/dht/weather', methods=['GET'])
def baidu_verify():
    print(f'请求方法: {request.method}')
    print(f'URL参数: {request.args}')
    print(f'请求头: {dict(request.headers)}')
    print(f'完整URL: {request.url}')
    print(f'查询字符串: {request.query_string.decode()}')
    return '35b6efa8616e4fbbc3f72e1476e367e139d97ab076a77ab5d1a0f3bcbe15d04b'

import json

# 全局变量用于缓存上次的温湿度数据
last_humidity_temperature = None

@api_v1.route('/dht/weather', methods=['POST'])
def show_weather_info():
    """
    接受DHT11传感器数据并解码处理

    接收包含base64编码温湿度数据的JSON，解码后返回结构化的温湿度信息
    如果数据与上次相同则忽略，否则更新飞书表格中的传感器数据

    Returns:
        JSON响应包含解码后的DHT11传感器数据
    """
    global last_humidity_temperature
    
    try:
        data = request.get_json()
        humidity_temperature = decode_dht11_message(data)
        data['message'] = humidity_temperature
        logger.debug(f"解码后的DHT11数据: {json.dumps(data)}")
        # 获取查询参数
        tenant_num = request.args.get('num') or 1
        # 检查数据是否与上次相同
        if last_humidity_temperature != humidity_temperature:
            # 数据有变化，更新飞书表格
            try:
                update_result = update_sensor_data_to_feishu(humidity_temperature, tenant_num)
                if update_result['success']:
                    logger.info(f"成功更新飞书传感器数据: {humidity_temperature}")
                    # 更新缓存
                    last_humidity_temperature = humidity_temperature
                else:
                    logger.error(f"更新飞书传感器数据失败: {update_result['message']}")
            except Exception as feishu_error:
                logger.error(f"更新飞书数据时发生异常: {str(feishu_error)}")
        else:
            logger.debug("温湿度数据与上次相同，跳过更新")
        
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

def update_sensor_data_to_feishu(humidity_temperature, tenant_num):
    """
    更新传感器数据到飞书表格
    
    Args:
        humidity_temperature: 包含温度和湿度的字典
        
    Returns:
        更新结果字典
    """
    try:
        # 1. 从数据表缓存中获取「传感器」表的所有记录
        records_result = tenant_service.get_tenant_feishu_service(tenant_num).get_table_records_new('传感器')
        if not records_result['success']:
            return {
                'success': False,
                'message': f"获取传感器表记录失败: {records_result['message']}"
            }
        
        records = records_result['data'].get('items', [])
        
        # 2. 找到名称为"温度"和"湿度"的记录ID
        temperature_record_id = None
        humidity_record_id = None
        for record in records:
            fields = record.get('fields', {})
            name = fields.get('名称', '')
            if name == '温度':
                temperature_record_id = record.get('record_id')
            elif name == '湿度':
                humidity_record_id = record.get('record_id')
        
        if not temperature_record_id or not humidity_record_id:
            return {
                'success': False,
                'message': f"未找到温度或湿度记录，温度ID: {temperature_record_id}, 湿度ID: {humidity_record_id}"
            }
        
        # 3. 准备批量更新的记录数据
        update_records = []
        
        # 更新温度记录
        if 'temperature' in humidity_temperature:
            update_records.append({
                'record_id': temperature_record_id,
                'fields': {
                    '文本': humidity_temperature['temperature']
                }
            })
        
        # 更新湿度记录
        if 'humidity' in humidity_temperature:
            update_records.append({
                'record_id': humidity_record_id,
                'fields': {
                    '文本': humidity_temperature['humidity']
                }
            })
        
        if not update_records:
            return {
                'success': False,
                'message': '没有有效的温湿度数据需要更新'
            }
        
        # 4. 调用批量更新接口
        update_result = feishu_service.batch_update_records('传感器', update_records)
        
        return update_result
        
    except Exception as e:
        return {
            'success': False,
            'message': f'更新传感器数据异常: {str(e)}'
        }


