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

    print("✓ 根路径测试通过\n")

def main():
    """运行所有测试"""
    print("开始API接口测试...")
    print("=" * 50)

    try:
        test_health_check()
        test_products_api()
        test_product_detail_api()
        test_root_endpoint()

        print("🎉 所有API测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    main()
