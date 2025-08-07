#!/usr/bin/env python3
"""
图片代理接口测试脚本
"""
import requests
import json
import sys
import os

def test_image_proxy():
    """测试图片代理接口"""
    base_url = "http://127.0.0.1:5000"
    
    print("开始图片代理接口测试...")
    print("=" * 50)
    
    # 1. 先获取农场数据，找到图片file_token
    print("=== 获取农场数据 ===")
    try:
        response = requests.get(f"{base_url}/api/v1/farm/info?product_id=recuT512gzx6yw")
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                farm_data = data['data']
                print("✓ 农场数据获取成功")
                
                # 查找图片file_token
                file_tokens = []
                
                # 检查首图
                if 'product_info' in farm_data and '首图' in farm_data['product_info']:
                    first_image = farm_data['product_info']['首图']
                    if isinstance(first_image, dict) and 'file_token' in first_image:
                        file_tokens.append(('首图', first_image['file_token']))
                
                # 检查饲喂记录图片
                if 'feeding_records' in farm_data:
                    for record in farm_data['feeding_records']:
                        if 'images' in record and record['images']:
                            for i, image in enumerate(record['images']):
                                if isinstance(image, dict) and 'file_token' in image:
                                    file_tokens.append((f"饲喂记录-{record['food_name']}-图片{i+1}", image['file_token']))
                
                # 检查养殖流程图片
                if 'breeding_process' in farm_data:
                    for process in farm_data['breeding_process']:
                        if 'images' in process and process['images']:
                            for i, image in enumerate(process['images']):
                                if isinstance(image, dict) and 'file_token' in image:
                                    file_tokens.append((f"养殖流程-{process['process_name']}-图片{i+1}", image['file_token']))
                
                print(f"找到 {len(file_tokens)} 个图片文件令牌")
                
                if not file_tokens:
                    print("❌ 没有找到任何图片文件令牌")
                    return False
                
            else:
                print(f"❌ 农场数据获取失败: {data['message']}")
                return False
        else:
            print(f"❌ 农场数据请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 农场数据请求异常: {str(e)}")
        return False
    
    # 2. 测试图片代理接口
    print("\n=== 测试图片代理接口 ===")
    success_count = 0
    
    for name, file_token in file_tokens:
        print(f"\n--- 测试 {name} ---")
        print(f"文件令牌: {file_token}")
        
        try:
            # 测试HEAD请求获取图片信息
            response = requests.head(f"{base_url}/api/v1/img/{file_token}", timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'unknown')
                content_length = response.headers.get('Content-Length', 'unknown')
                cache_control = response.headers.get('Cache-Control', 'none')
                
                print(f"✓ 图片代理成功")
                print(f"  Content-Type: {content_type}")
                print(f"  Content-Length: {content_length} bytes")
                print(f"  Cache-Control: {cache_control}")
                
                success_count += 1
                
                # 测试实际下载（只下载前1KB验证）
                try:
                    response = requests.get(f"{base_url}/api/v1/img/{file_token}", 
                                          headers={'Range': 'bytes=0-1023'}, 
                                          timeout=5)
                    if response.status_code in [200, 206]:
                        print(f"  ✓ 图片数据下载验证成功")
                    else:
                        print(f"  ⚠ 图片数据下载验证失败，状态码: {response.status_code}")
                except Exception as e:
                    print(f"  ⚠ 图片数据下载验证异常: {str(e)}")
                
            else:
                print(f"❌ 图片代理失败，状态码: {response.status_code}")
                if response.headers.get('Content-Type') == 'application/json':
                    try:
                        error_data = response.json()
                        print(f"  错误信息: {error_data.get('message', '未知错误')}")
                    except:
                        pass
                        
        except requests.exceptions.Timeout:
            print(f"❌ 图片代理超时")
        except Exception as e:
            print(f"❌ 图片代理异常: {str(e)}")
    
    # 3. 测试结果统计
    print(f"\n=== 测试结果统计 ===")
    total_tests = len(file_tokens)
    print(f"总测试数: {total_tests}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_tests - success_count}")
    print(f"成功率: {success_count/total_tests*100:.1f}%" if total_tests > 0 else "成功率: 0%")
    
    # 4. 测试错误情况
    print(f"\n=== 测试错误情况 ===")
    
    # 测试无效的file_token
    print("--- 测试无效file_token ---")
    try:
        response = requests.get(f"{base_url}/api/v1/img/invalid_token", timeout=5)
        if response.status_code != 200:
            print(f"✓ 无效file_token正确返回错误，状态码: {response.status_code}")
        else:
            print(f"❌ 无效file_token应该返回错误，但返回了: {response.status_code}")
    except Exception as e:
        print(f"⚠ 无效file_token测试异常: {str(e)}")
    
    print(f"\n🎉 图片代理接口测试完成！")
    return success_count == total_tests

if __name__ == "__main__":
    success = test_image_proxy()
    sys.exit(0 if success else 1)
