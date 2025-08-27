#!/usr/bin/env python3
"""测试运行脚本

运行多租户功能的所有测试用例
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """运行所有测试"""
    # 发现并运行测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()

def run_specific_test(test_module):
    """运行特定的测试模块
    
    Args:
        test_module: 测试模块名称，如 'test_multi_tenant'
    """
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='运行多租户功能测试')
    parser.add_argument('--module', '-m', help='运行特定的测试模块')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有可用的测试模块')
    
    args = parser.parse_args()
    
    if args.list:
        print("可用的测试模块:")
        test_dir = os.path.join(os.path.dirname(__file__), 'tests')
        for file in os.listdir(test_dir):
            if file.startswith('test_') and file.endswith('.py'):
                module_name = file[:-3]  # 移除.py扩展名
                print(f"  - {module_name}")
    elif args.module:
        print(f"运行测试模块: {args.module}")
        success = run_specific_test(args.module)
        sys.exit(0 if success else 1)
    else:
        print("运行所有测试...")
        success = run_tests()
        sys.exit(0 if success else 1)