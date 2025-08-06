"""
API接口测试
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health_check():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 0
    assert data['data']['status'] == 'healthy'
    
    print("✓ 健康检查接口测试通过\n")

def test_products_api():
    """测试产品列表接口"""
    print("=== 测试产品列表接口 ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/products")
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['code'] == 0
    assert 'products' in data['data']
    assert isinstance(data['data']['products'], list)
    
    # 检查产品数据结构
    if data['data']['products']:
        product = data['data']['products'][0]
        required_fields = ['product_id', 'product_name', 'app_token', 'auth_code']
        for field in required_fields:
            assert field in product, f"缺少字段: {field}"
    
    print("✓ 产品列表接口测试通过\n")

def test_product_detail_api():
    """测试产品详情接口"""
    print("=== 测试产品详情接口 ===")

    # 首先获取一个有效的产品ID
    products_response = requests.get(f"{BASE_URL}/api/v1/products")
    assert products_response.status_code == 200

    products_data = products_response.json()
    if products_data['data']['products']:
        product_id = products_data['data']['products'][0]['product_id']
        print(f"使用产品ID: {product_id}")

        # 测试获取产品详情
        response = requests.get(f"{BASE_URL}/api/v1/product/{product_id}")

        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 0
        assert 'data' in data

        # 检查产品详情数据结构
        product_detail = data['data']
        required_fields = ['product_id', 'product_name', 'app_token', 'auth_code']
        for field in required_fields:
            assert field in product_detail, f"缺少字段: {field}"

        print("✓ 产品详情接口测试通过")
    else:
        print("⚠ 没有可用的产品数据，跳过详情测试")

    # 测试不存在的产品ID
    print("\n--- 测试不存在的产品ID ---")
    response = requests.get(f"{BASE_URL}/api/v1/product/invalid_id")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 500  # 飞书API返回错误
    data = response.json()
    assert data['code'] == 1

    print("✓ 无效产品ID测试通过\n")

def test_farm_tables_api():
    """测试农户数据表列表接口"""
    print("=== 测试农户数据表列表接口 ===")

    # 首先获取一个有效的产品ID
    products_response = requests.get(f"{BASE_URL}/api/v1/products")
    assert products_response.status_code == 200

    products_data = products_response.json()
    if products_data['data']['products']:
        product_id = products_data['data']['products'][0]['product_id']
        print(f"使用产品ID: {product_id}")

        # 测试获取农户数据表列表
        response = requests.get(f"{BASE_URL}/api/v1/farm/tables?product_id={product_id}")

        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 0
        assert 'data' in data

        # 检查数据结构
        farm_data = data['data']
        assert 'farmer_info' in farm_data
        assert 'tables' in farm_data
        assert 'total' in farm_data

        # 检查农户信息
        farmer_info = farm_data['farmer_info']
        required_farmer_fields = ['product_id', 'farmer_name', 'app_token']
        for field in required_farmer_fields:
            assert field in farmer_info, f"农户信息缺少字段: {field}"

        # 检查数据表信息
        tables = farm_data['tables']
        assert isinstance(tables, list)
        if tables:
            table = tables[0]
            required_table_fields = ['table_id', 'table_name', 'revision']
            for field in required_table_fields:
                assert field in table, f"数据表信息缺少字段: {field}"

        print("✓ 农户数据表列表接口测试通过")
    else:
        print("⚠ 没有可用的产品数据，跳过数据表测试")

    # 测试缺少product_id参数
    print("\n--- 测试缺少product_id参数 ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/tables")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 1
    assert '缺少必要参数' in data['message']

    print("✓ 缺少参数测试通过")

    # 测试无效的product_id
    print("\n--- 测试无效的product_id ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/tables?product_id=invalid_id")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 404
    data = response.json()
    assert data['code'] == 1

    print("✓ 无效product_id测试通过\n")

def test_farm_info_api():
    """测试农户完整信息接口"""
    print("=== 测试农户完整信息接口 ===")

    # 首先获取一个有效的产品ID
    products_response = requests.get(f"{BASE_URL}/api/v1/products")
    assert products_response.status_code == 200

    products_data = products_response.json()
    if products_data['data']['products']:
        product_id = products_data['data']['products'][0]['product_id']
        print(f"使用产品ID: {product_id}")

        # 测试获取农户完整信息
        response = requests.get(f"{BASE_URL}/api/v1/farm/info?product_id={product_id}")

        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 0
        assert 'data' in data

        # 检查数据结构
        farm_data = data['data']
        required_fields = ['farmer_info', 'product_info', 'feeding_records', 'breeding_process', 'statistics']
        for field in required_fields:
            assert field in farm_data, f"缺少字段: {field}"

        # 检查农户信息
        farmer_info = farm_data['farmer_info']
        required_farmer_fields = ['product_id', 'farmer_name', 'app_token']
        for field in required_farmer_fields:
            assert field in farmer_info, f"农户信息缺少字段: {field}"

        # 检查统计信息
        statistics = farm_data['statistics']
        required_stats_fields = ['feeding_count', 'process_count']
        for field in required_stats_fields:
            assert field in statistics, f"统计信息缺少字段: {field}"

        # 检查饲喂记录格式
        feeding_records = farm_data['feeding_records']
        assert isinstance(feeding_records, list)
        if feeding_records:
            record = feeding_records[0]
            required_record_fields = ['record_id', 'food_name', 'operator', 'operation_time_formatted']
            for field in required_record_fields:
                assert field in record, f"饲喂记录缺少字段: {field}"

        # 检查养殖流程格式
        breeding_process = farm_data['breeding_process']
        assert isinstance(breeding_process, list)
        if breeding_process:
            process = breeding_process[0]
            required_process_fields = ['record_id', 'process_name', 'operation_time_formatted']
            for field in required_process_fields:
                assert field in process, f"养殖流程缺少字段: {field}"

        print("✓ 农户完整信息接口测试通过")
    else:
        print("⚠ 没有可用的产品数据，跳过完整信息测试")

    # 测试缺少product_id参数
    print("\n--- 测试缺少product_id参数 ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/info")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 1
    assert '缺少必要参数' in data['message']

    print("✓ 缺少参数测试通过\n")

def test_table_fields_api():
    """测试数据表字段定义接口"""
    print("=== 测试数据表字段定义接口 ===")

    # 首先获取一个有效的产品ID
    products_response = requests.get(f"{BASE_URL}/api/v1/products")
    assert products_response.status_code == 200

    products_data = products_response.json()
    if products_data['data']['products']:
        product_id = products_data['data']['products'][0]['product_id']
        print(f"使用产品ID: {product_id}")

        # 获取数据表列表
        tables_response = requests.get(f"{BASE_URL}/api/v1/farm/tables?product_id={product_id}")
        assert tables_response.status_code == 200

        tables_data = tables_response.json()
        if tables_data['data']['tables']:
            table_name = tables_data['data']['tables'][0]['table_name']
            print(f"使用表名: {table_name}")

            # 测试获取字段定义
            import urllib.parse
            encoded_table_name = urllib.parse.quote(table_name)
            response = requests.get(f"{BASE_URL}/api/v1/farm/table/fields?product_id={product_id}&tname={encoded_table_name}")

            print(f"状态码: {response.status_code}")
            print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

            assert response.status_code == 200
            data = response.json()
            assert data['code'] == 0
            assert 'data' in data

            # 检查数据结构
            fields_data = data['data']
            required_fields = ['table_info', 'farmer_info', 'fields', 'total']
            for field in required_fields:
                assert field in fields_data, f"缺少字段: {field}"

            # 检查表信息
            table_info = fields_data['table_info']
            required_table_fields = ['table_id', 'table_name', 'revision']
            for field in required_table_fields:
                assert field in table_info, f"表信息缺少字段: {field}"

            # 检查字段定义
            fields = fields_data['fields']
            assert isinstance(fields, list)
            if fields:
                field = fields[0]
                required_field_fields = ['field_id', 'field_name', 'type', 'is_primary']
                for field_attr in required_field_fields:
                    assert field_attr in field, f"字段定义缺少属性: {field_attr}"

            print("✓ 数据表字段定义接口测试通过")
        else:
            print("⚠ 没有可用的数据表，跳过字段定义测试")
    else:
        print("⚠ 没有可用的产品数据，跳过字段定义测试")

    # 测试缺少product_id参数
    print("\n--- 测试缺少product_id参数 ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/table/fields?tname=商品")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 1
    assert '缺少必要参数' in data['message']

    print("✓ 缺少product_id参数测试通过")

    # 测试缺少tname参数
    print("\n--- 测试缺少tname参数 ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/table/fields?product_id=recuT512gzx6yw")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 1
    assert '缺少必要参数' in data['message']

    print("✓ 缺少tname参数测试通过")

    # 测试不存在的表名
    print("\n--- 测试不存在的表名 ---")
    response = requests.get(f"{BASE_URL}/api/v1/farm/table/fields?product_id=recuT512gzx6yw&tname=不存在的表")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 404
    data = response.json()
    assert data['code'] == 1
    assert '未找到名称为' in data['message']

    print("✓ 不存在表名测试通过\n")

def test_root_endpoint():
    """测试根路径"""
    print("=== 测试根路径 ===")

    response = requests.get(f"{BASE_URL}/")

    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert 'endpoints' in data
    assert 'product_detail' in data['endpoints']
    assert 'farm_tables' in data['endpoints']
    assert 'farm_info' in data['endpoints']
    assert 'table_fields' in data['endpoints']

    print("✓ 根路径测试通过\n")

def main():
    """运行所有测试"""
    print("开始API接口测试...")
    print("=" * 50)

    try:
        test_health_check()
        test_products_api()
        test_product_detail_api()
        test_farm_tables_api()
        test_farm_info_api()
        test_table_fields_api()
        test_root_endpoint()

        print("🎉 所有API测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    main()
