#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API测试文件
演示FeishuApi类的基本使用方法
"""

from feishu_api import FeishuApi


def test_feishu_api():
    """
    测试飞书API基本功能
    注意：需要替换为真实的app_token和personal_token
    """
    
    # 初始化API客户端
    app_token = "L2LwbebNLa3nFnsnZelcBaWInGf"
    personal_token = "pt-XY3suieVxgZldqT_RaF-FJQM7qJfe-2cYEEhpWiYAQAAHABAsANABag7g5PO"
    
    api = FeishuApi(app_token=app_token, personal_token=personal_token)

if __name__ == "__main__":
    test_feishu_api()
