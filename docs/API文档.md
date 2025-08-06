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

### 3. 获取农户数据表列表

**接口地址**: `GET /api/v1/farm/tables?product_id={id}`

**查询参数**:
- `product_id`: 产品ID（必填）

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "farmer_info": {
      "product_id": "recuT512gzx6yw",
      "farmer_name": "张三",
      "app_token": "KnOFbTu1harM6wsNbWdcro2Rnoc"
    },
    "tables": [
      {
        "table_id": "tblELkotV4rh2PCz",
        "table_name": "商品",
        "revision": 25
      },
      {
        "table_id": "tblct3YtuqdyA6VW",
        "table_name": "饲喂记录",
        "revision": 9
      },
      {
        "table_id": "tblu6cwfWjeFI0Vv",
        "table_name": "养殖流程",
        "revision": 7
      }
    ],
    "total": 3,
    "has_more": false,
    "page_token": "tblu6cwfWjeFI0Vv"
  }
}
```

**错误响应**:
- `400`: 缺少product_id参数或农户缺少API配置
- `404`: 产品不存在
- `500`: 服务器内部错误

### 4. 获取农户完整信息

**接口地址**: `GET /api/v1/farm/info?product_id={id}`

**查询参数**:
- `product_id`: 产品ID（必填）

**功能说明**: 获取静态页面所需的完整数据，包括商品信息、饲喂记录、养殖流程等

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "farmer_info": {
      "product_id": "recuT512gzx6yw",
      "farmer_name": "张三",
      "app_token": "KnOFbTu1harM6wsNbWdcro2Rnoc"
    },
    "product_info": {
      "标题": {
        "value": "云南泽铁苗寨土鸡",
        "images": []
      },
      "商品名称": {
        "value": "农家散养土鸡",
        "images": []
      },
      "是否有机": {
        "value": "有机",
        "images": []
      },
      "国产/进口": {
        "value": "国产",
        "images": []
      },
      "饲养农户": {
        "value": "张三",
        "images": []
      },
      "养殖企业": {
        "value": "昆明远纳农业发展有限公司",
        "images": []
      },
      "第一次查询时间": {
        "value": "2025-07-01 18:45:16",
        "images": []
      }
    },
    "feeding_records": [
      {
        "record_id": "recuT3qmhcV0NP",
        "food_name": "玉米",
        "operator": "张三",
        "operation_time": 1754444961181,
        "operation_time_formatted": "2025-08-06 09:49:21",
        "created_time": 1754444961000,
        "created_time_formatted": "2025-08-06 09:49:21",
        "updated_time": 1754449882000,
        "images": []
      }
    ],
    "breeding_process": [
      {
        "record_id": "recuT3qqrOJGkM",
        "process_name": "绑定",
        "operation_time": 1754444967842,
        "operation_time_formatted": "2025-08-06 09:49:27",
        "created_time": 1754444968000,
        "created_time_formatted": "2025-08-06 09:49:28",
        "updated_time": 1754445009000,
        "images": []
      }
    ],
    "statistics": {
      "feeding_count": 1,
      "process_count": 1
    }
  }
}
```

**错误响应**:
- `400`: 缺少product_id参数或农户缺少API配置
- `404`: 产品不存在
- `500`: 服务器内部错误

### 5. 获取数据表字段定义（Admin接口）

**接口地址**: `GET /api/v1/farm/table/fields?product_id={id}&tname={table_name}`

**查询参数**:
- `product_id`: 产品ID（必填）
- `tname`: 数据表名称（必填）

**功能说明**: 获取指定数据表的字段定义，用于管理和开发目的

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "table_info": {
      "table_id": "tblELkotV4rh2PCz",
      "table_name": "商品",
      "revision": 25
    },
    "farmer_info": {
      "farmer_name": "张三",
      "product_id": "recuT512gzx6yw"
    },
    "fields": [
      {
        "field_id": "fldJXi04FC",
        "field_name": "名称",
        "type": 1,
        "property": null,
        "description": "",
        "is_primary": true
      },
      {
        "field_id": "fldKes408E",
        "field_name": "分组",
        "type": 1,
        "property": null,
        "description": "",
        "is_primary": false
      },
      {
        "field_id": "fld8Zu8H4r",
        "field_name": "文本",
        "type": 1,
        "property": null,
        "description": "",
        "is_primary": false
      },
      {
        "field_id": "fldyhqoFsR",
        "field_name": "顺序",
        "type": 2,
        "property": {
          "formatter": "0"
        },
        "description": "",
        "is_primary": false
      },
      {
        "field_id": "flds6ik0IA",
        "field_name": "图片",
        "type": 17,
        "property": null,
        "description": "",
        "is_primary": false
      }
    ],
    "total": 6,
    "has_more": false,
    "page_token": "flds6ik0IA"
  }
}
```

**字段类型说明**:
- `1`: 文本
- `2`: 数字
- `5`: 日期时间
- `17`: 图片
- `1002`: 修改时间

**错误响应**:
- `400`: 缺少必要参数
- `404`: 产品不存在或数据表不存在
- `500`: 服务器内部错误

### 6. 健康检查

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

# 获取农户数据表列表
curl -X GET "http://127.0.0.1:5000/api/v1/farm/tables?product_id=recuT512gzx6yw"

# 获取农户完整信息
curl -X GET "http://127.0.0.1:5000/api/v1/farm/info?product_id=recuT512gzx6yw"

# 获取数据表字段定义
curl -X GET "http://127.0.0.1:5000/api/v1/farm/table/fields?product_id=recuT512gzx6yw&tname=商品"

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

// 获取农户数据表列表
fetch('http://127.0.0.1:5000/api/v1/farm/tables?product_id=recuT512gzx6yw')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取农户完整信息
fetch('http://127.0.0.1:5000/api/v1/farm/info?product_id=recuT512gzx6yw')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取数据表字段定义
fetch('http://127.0.0.1:5000/api/v1/farm/table/fields?product_id=recuT512gzx6yw&tname=商品')
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
