# 农产品溯源系统

基于飞书多维表格的农产品溯源系统，支持农户数据管理和产品信息展示。

## todo：待办任务
系统管理
- [ ] 权限管理：
  - [ ] 授权列表：存储每个养殖企业的app_token、授权码、授权农户数量。
  - [ ] 防止其他人对推流服务进行恶意调用，推流服务鉴权。
- [ ] 图片压缩服务
- [ ] sqlite 缓存
- [ ] 图片可点击放大
- [ ] 多张图片可切换
- [ ] 图片压缩后显示
- [ ] 支持时间相关的格式化（使用缓存）。
- [ ] 步数模拟：模拟其他农户的步数变化。
- [ ] 打包可运行的程序，部署上线。
- [ ] 客户培训：相关使用文档编写。

## 技术栈

- **后端**: Python Flask
- **前端**: HTML + CSS + petite-vue
- **数据存储**: 飞书多维表格
- **API**: 飞书开放平台API

## 开发说明

### 数据流程
1. 用户访问页面时携带产品ID（农户管理数据表 的record_id）
2. 后端根据产品ID查询农户管理表获取农户信息
3. 分别获取传感器、饲喂记录、养殖流程表的数据
4. 前端使用petite-vue动态渲染数据

### 飞书表格结构
- **授权列表**: 存储每个养殖企业的app_token、授权码、授权农户数量。
- **传感器**: 存储传感器数据。
- **农户管理**: 一个农户对应一个页面的数据。
- **饲喂记录**: 存储饲喂操作记录。
- **养殖流程**: 存储养殖流程节点信息。


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

## 部署上线

### 拷贝代码
使用 rsync 拷贝运行所需的代码到服务器
```bash
# 同步代码到服务器，排除不需要的文件和目录
rsync -avz --exclude-from='.gitignore' \
  --exclude='docs/' \
  --exclude='tests/' \
  --exclude='.git/' \
  --exclude='.gitignore' \
  --exclude='README.md' \
  --exclude='*.md' \
  ./ pxact:/root/projects/farm/

# 参数说明：
# -a: 归档模式，保持文件属性
# -v: 详细输出
# -z: 压缩传输
# --delete: 删除目标目录中源目录没有的文件
# --exclude-from: 从 .gitignore 文件读取排除规则
# --exclude: 额外排除指定的文件或目录
```

### 运行

安装依赖
```bash
cd backend && pip install -r requirements.txt
```

配置环境变量
```bash
cp config/.env.example config/.env
# 编辑 config/.env 文件，填入飞书API相关配置
```

前台运行：
```bash
cd backend && python app.py
```

后台运行：
```bash
nohup cd backend && python app.py > app.log 2>&1 &
```

### 远程调试技巧

使用 ssh 隧道
```bash
# 本地端口转发
ssh -L 5000:localhost:5000 pxact
```