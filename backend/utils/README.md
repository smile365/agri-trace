# 工具类说明

## 时间格式化工具 (TimeFormatter)

### 概述

`TimeFormatter` 是一个专门用于处理微秒时间戳格式化的工具类，特别适用于处理飞书API返回的时间戳数据。

### 主要功能

- 将微秒时间戳转换为各种日期格式
- 支持多种预定义格式和自定义格式
- 提供时间戳验证功能
- 包含错误处理机制
- 支持中文日期格式

### 使用方法

#### 1. 基本使用

```python
from utils.time_formatter import TimeFormatter

# 微秒时间戳（飞书API格式）
timestamp = 1640995200000000  # 2022-01-01 08:00:00

# 格式化为标准日期时间
result = TimeFormatter.format_timestamp(timestamp, 'yyyy-MM-dd HH:mm:ss')
print(result)  # 输出: 2022-01-01 08:00:00

# 格式化为中文日期
result = TimeFormatter.format_timestamp(timestamp, 'yyyy年MM月dd日')
print(result)  # 输出: 2022年01月01日
```

#### 2. 便捷函数

```python
from utils.time_formatter import format_microsecond_timestamp, get_current_formatted_time

# 使用便捷函数格式化
result = format_microsecond_timestamp(timestamp, 'yyyy/MM/dd')
print(result)  # 输出: 2022/01/01

# 获取当前时间
current = get_current_formatted_time('yyyy-MM-dd HH:mm')
print(current)  # 输出: 2025-08-27 22:17
```

#### 3. 支持的格式

**预定义格式：**
- `yyyy-MM-dd HH:mm:ss` - 标准日期时间
- `yyyy/MM/dd HH:mm` - 斜杠分隔日期时间
- `yyyy-MM-dd` - 仅日期
- `HH:mm:ss` - 仅时间
- `yyyy年MM月dd日` - 中文日期
- `MM/dd/yyyy` - 美式日期
- `dd/MM/yyyy` - 欧式日期
- 更多格式请查看 `TimeFormatter.get_supported_formats()`

**自定义格式：**
- `yyyy` - 四位年份
- `yy` - 两位年份
- `MM` - 两位月份
- `dd` - 两位日期
- `HH` - 24小时制小时
- `mm` - 分钟
- `ss` - 秒

#### 4. 错误处理

```python
# 验证时间戳
is_valid = TimeFormatter.validate_timestamp(timestamp)
print(is_valid)  # 输出: True

# 处理无效时间戳
result = TimeFormatter.format_timestamp('invalid', 'yyyy-MM-dd')
print(result)  # 输出: None
```

#### 5. 飞书集成示例

```python
# 模拟飞书API返回的数据
feishu_data = {
    'created_time': '1640995200000000',  # 字符串格式
    'updated_time': 1641081600000000,    # 数字格式
}

# 根据字段配置格式化
date_formatters = {
    'created_time': 'yyyy-MM-dd HH:mm',
    'updated_time': 'yyyy/MM/dd',
}

for field, timestamp in feishu_data.items():
    formatter = date_formatters.get(field, 'yyyy-MM-dd HH:mm:ss')
    formatted = TimeFormatter.format_timestamp(timestamp, formatter)
    print(f"{field}: {formatted}")
```

### 文件结构

- `time_formatter.py` - 主要工具类
- `time_formatter_example.py` - 使用示例和测试代码
- `README.md` - 本说明文档

### 注意事项

1. 输入的时间戳必须是微秒级别（飞书API标准）
2. 无效的时间戳会返回 `None`
3. 支持字符串和数字类型的时间戳输入
4. 时间戳验证范围为1970年到2100年
5. 中文格式需要使用预定义格式或正确的格式字符串

### 性能说明

- 预定义格式性能最佳（直接映射）
- 自定义格式使用正则表达式转换
- 支持批量处理大量时间戳数据
- 包含缓存机制以提高重复格式化性能