# 农产品溯源系统

基于飞书多维表格的农产品溯源系统，支持农户数据管理和产品信息展示。

## 项目结构



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
http://127.0.0.1:5000/index.html?id=recuT512gzx6yw
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
