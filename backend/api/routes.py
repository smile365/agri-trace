"""
API路由定义
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, Response
from services.tenant_service import tenant_service
from utils.lot_decode import temperature_humidity2json,decode_bdlot_msg
import logging
import requests
from config import config
from urllib.parse import parse_qs, urlparse
from api.bdlot import bd_lot_cache


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
            feeding_records = data.get('feeding_records', [])
            # 处理养殖流程时间格式
            breeding_process = data.get('breeding_process', [])

            # 处理产品信息中的封面图和监控地址格式
            product_info = data.get('product_info', {}).copy()
            
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
            statistics = data.get('statistics')
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
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"获取农户完整信息异常: {str(e)}")

        error_response = {
            'code': 1,
            'message': f'服务器内部错误: {str(e)}',
            'data': None
        }

        return jsonify(error_response), 500

@api_v1.route('/bdlot/<tenant_num>/receive', methods=['GET','POST'])
def receive_baidu_lot_data(tenant_num):
    """
    接收百度智能云 lot 数据接口
    Returns:
        JSON响应表示服务状态
    """
    if request.method == 'GET':
        qs = bd_lot_cache.set(request.url, request.query_string.decode())
        print(f'验证字符串: {qs}')
        return bd_lot_cache.get(request.url)
    #print(request.get_json())
    original_data = decode_bdlot_msg(request.get_json())
    #print(f'original_data: {original_data}')
    #print(f"传感器数据: {sensor_data}")
    if type(original_data) == str:
        return save_weather_info(tenant_num, original_data)
    sensor_data = original_data['sensor_data']
    tenant_service.save_baidu_lot_data(tenant_num, sensor_data)
    return jsonify({
        'code': 200,
        'msg': 'ok'
    }), 200

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
        tenant_num = request.args.get('num') or '2'
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
    print(f'请求方法: {request.method}')
    print(f'URL参数: {request.args}')
    print(f'请求头: {dict(request.headers)}')
    print(f'完整URL: {request.url}')
    print(f'查询字符串: {request.query_string.decode()}')
    
    # 如果是POST请求，打印请求体
    if request.method == 'GET':
        qs = bd_lot_cache.set(request.url, request.query_string.decode())
        print(f'验证字符串: {qs}')
        return bd_lot_cache.get(request.url)
    elif request.method == 'POST':
        #print(f'Content-Type: {request.content_type}')
        if request.is_json:
            original_data = decode_baidu_lot_message(request.get_json())
            sensor_data = original_data['sensor_data']
            print(f"传感器数据: {sensor_data}")
        elif request.form:
            print(f'表单数据: {request.form}')
        else:
            print(f'原始数据: {request.get_data().decode()}')
    
    return 'ok'

last_humidity_temperature_key = 'humidity_temperature'
def save_weather_info(tenant_num:str, original_data):
    try:
        last_humidity_temperature = bd_lot_cache.getv(last_humidity_temperature_key)
        if last_humidity_temperature == original_data:
            return 'ok'
        humidity_temperature = temperature_humidity2json(original_data)
        # 检查数据是否与上次相同
        if update_sensor_data_to_feishu(humidity_temperature, tenant_num):
            bd_lot_cache.setv(last_humidity_temperature_key, original_data)
    except Exception as e:
        logger.error(f"DHT11数据解码失败: {str(e)}")
    return 'ok'
       

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
        feishu_service = tenant_service.get_tenant_feishu_service(tenant_num)
        records_result = feishu_service.get_table_records('传感器')
        if not records_result['success']:
            logger.error(f"获取传感器表记录失败: {records_result['message']}")
            return False
        records = records_result.get('data',{}).get('items', [])
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
            logger.error(f"未找到温度或湿度记录，温度ID: {temperature_record_id}, 湿度ID: {humidity_record_id}")
            return False
        # 3. 准备批量更新的记录数据
        update_records = []
        
        # 更新温度记录
        if 'temperature' in humidity_temperature:
            update_records.append({
                'record_id': temperature_record_id,
                'fields': {
                    '数据': humidity_temperature['temperature']
                }
            })
        
        # 更新湿度记录
        if 'humidity' in humidity_temperature:
            update_records.append({
                'record_id': humidity_record_id,
                'fields': {
                    '数据': humidity_temperature['humidity']
                }
            })
        
        if not update_records:
            return
        # 4. 调用批量更新接口
        update_result = feishu_service.batch_update_records('传感器', update_records)
        return update_result.get('success', False)
        
    except Exception as e:
        logger.error(f"更新传感器数据异常: {str(e)}")
        return False


