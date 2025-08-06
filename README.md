# 农产品溯源系统

基于飞书多维表格的农产品溯源系统，支持农户数据管理和产品信息展示。

## 项目结构

```
farm/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖包列表
├── config/                      # 配置文件目录
│   ├── .env                     # 环境变量配置
│   └── .env.example             # 环境变量配置模板
├── backend/                     # 后端代码目录
│   ├── api/                     # API接口
│   │   ├── __init__.py
│   │   ├── fs_demo.py           # 飞书API测试文件
│   │   └── routes.py            # 路由定义
│   ├── services/                # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── feishu_service.py    # 飞书API服务
│   │   └── data_service.py      # 数据处理服务
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── farmer.py            # 农户模型
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   └── helpers.py           # 辅助函数
│   └── app.py                   # Flask应用入口
├── frontend/                    # 前端代码目录
│   ├── templates/               # HTML模板
│   │   └── index.html           # 主页面
│   └── static/                  # 静态资源
│       ├── css/
│       │   └── style.css        # 样式文件
│       ├── js/
│       │   └── main.js          # JavaScript文件
│       └── images/              # 图片资源
├── docs/                        # 文档目录
│   ├── 功能清单.md              # 功能清单
│   └── 飞书多维表格接口.md      # 飞书API文档
└── tests/                       # 测试文件目录
    ├── __init__.py
    ├── test_api.py              # API测试
    └── test_services.py         # 服务测试
```

## 技术栈

- **后端**: Python Flask
- **前端**: HTML + CSS + petite-vue
- **数据存储**: 飞书多维表格
- **API**: 飞书开放平台API

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp config/.env.example config/.env
# 编辑 config/.env 文件，填入飞书API相关配置
```

3. 运行后端服务
```bash
cd backend
python app.py
```

4. 访问前端页面
```
http://localhost:5000?product_id=xxx
```

## 开发说明

### 数据流程
1. 用户访问页面时携带产品ID（农户列表的record_id）
2. 后端根据产品ID查询农户列表表获取农户信息
3. 使用农户的app_token和授权码获取该农户的数据表列表
4. 分别获取商品、饲喂记录、养殖流程表的数据
5. 前端使用petite-vue动态渲染数据

### 飞书表格结构
- **农户列表**: 存储农户基本信息和API访问凭证
- **商品**: 存储商品基本信息
- **饲喂记录**: 存储饲喂操作记录
- **养殖流程**: 存储养殖流程节点信息
