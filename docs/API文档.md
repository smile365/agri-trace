# 农产品溯源系统 API 文档

## 基础信息

- **基础URL**: `http://127.0.0.1:5000`
- **版本**: v1.0.0
- **数据格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误响应
```json
{
  "code": 1,
  "message": "错误信息",
  "data": null
}
```

## API 接口列表

### 1. 获取产品列表

**接口地址**: `GET /api/v1/products`

**请求参数**: 无

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "products": [
      {
        "product_id": "recuT512gzx6yw",
        "product_name": "张三",
        "app_token": "KnOFbTu1harM6wsNbWdcro2Rnoc",
        "auth_code": "pt-eHTfXM5N-Z_DP5H4UdggH4sjyPpfe-2cYHO0kmiYAQAAHABAsAKAC47s_BN9",
        "created_time": null,
        "last_modified_time": null
      }
    ],
    "total": 1,
    "has_more": false
  }
}
```

### 2. 获取产品详情

**接口地址**: `GET /api/v1/product/{id}`

**路径参数**:
- `id`: 产品ID（必填）

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "product_id": "recuT512gzx6yw",
    "product_name": "张三",
    "app_token": "KnOFbTu1harM6wsNbWdcro2Rnoc",
    "auth_code": "pt-eHTfXM5N-Z_DP5H4UdggH4sjyPpfe-2cYHO0kmiYAQAAHABAsAKAC47s_BN9",
    "contact": "",
    "address": "",
    "created_time": null,
    "last_modified_time": null,
    "created_by": null,
    "last_modified_by": null
  }
}
```

**错误响应**:
- `404`: 产品不存在
- `400`: 产品ID格式错误
- `500`: 服务器内部错误

### 3. 健康检查

**接口地址**: `GET /api/v1/health`

**请求参数**: 无

**响应示例**:
```json
{
  "code": 0,
  "message": "API服务运行正常",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

## 使用示例

### curl 命令示例

```bash
# 获取产品列表
curl -X GET "http://127.0.0.1:5000/api/v1/products"

# 获取产品详情
curl -X GET "http://127.0.0.1:5000/api/v1/product/recuT512gzx6yw"

# 健康检查
curl -X GET "http://127.0.0.1:5000/api/v1/health"
```

### JavaScript 示例

```javascript
// 获取产品列表
fetch('http://127.0.0.1:5000/api/v1/products')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取产品详情
fetch('http://127.0.0.1:5000/api/v1/product/recuT512gzx6yw')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 数据来源

所有产品数据来源于飞书多维表格「农户列表」，通过飞书开放平台API获取。

## 错误码说明

- `0`: 成功
- `1`: 业务错误（具体错误信息见message字段）
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误
