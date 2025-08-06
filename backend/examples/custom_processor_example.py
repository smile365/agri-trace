"""
自定义数据表处理器示例
演示如何为新的数据表类型注册自定义处理器
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.feishu_service import feishu_service

def process_equipment_table(records):
    """
    设备表处理器示例
    
    Args:
        records: 设备表记录列表
        
    Returns:
        处理后的设备信息列表
    """
    equipment_list = []
    for record in records:
        fields = record.get('fields', {})
        equipment_info = {
            'record_id': record.get('record_id'),
            'equipment_name': fields.get('设备名称', ''),
            'equipment_type': fields.get('设备类型', ''),
            'model': fields.get('型号', ''),
            'manufacturer': fields.get('制造商', ''),
            'install_date': fields.get('安装日期'),
            'status': fields.get('状态', ''),
            'location': fields.get('位置', ''),
            'maintenance_records': fields.get('维护记录', []),
            'images': fields.get('图片', []) if isinstance(fields.get('图片'), list) else []
        }
        equipment_list.append(equipment_info)
    
    return equipment_list

def process_inspection_table(records):
    """
    检查记录表处理器示例
    
    Args:
        records: 检查记录表记录列表
        
    Returns:
        处理后的检查记录列表
    """
    inspection_list = []
    for record in records:
        fields = record.get('fields', {})
        inspection_info = {
            'record_id': record.get('record_id'),
            'inspection_date': fields.get('检查日期'),
            'inspector': fields.get('检查员', ''),
            'inspection_type': fields.get('检查类型', ''),
            'result': fields.get('检查结果', ''),
            'issues_found': fields.get('发现问题', ''),
            'corrective_actions': fields.get('纠正措施', ''),
            'next_inspection': fields.get('下次检查日期'),
            'images': fields.get('图片', []) if isinstance(fields.get('图片'), list) else []
        }
        inspection_list.append(inspection_info)
    
    return inspection_list

def register_custom_processors():
    """注册自定义处理器"""
    print("注册自定义数据表处理器...")
    
    # 注册设备表处理器
    feishu_service.register_table_processor('设备', process_equipment_table)
    feishu_service.register_table_processor('equipment', process_equipment_table)
    
    # 注册检查记录表处理器
    feishu_service.register_table_processor('检查记录', process_inspection_table)
    feishu_service.register_table_processor('inspection', process_inspection_table)
    
    print("✓ 自定义处理器注册完成")

def show_registered_processors():
    """显示所有已注册的处理器"""
    print("\n=== 已注册的数据表处理器 ===")
    processors = feishu_service.get_registered_processors()
    
    for table_name, processor in processors.items():
        processor_name = processor.__name__ if hasattr(processor, '__name__') else str(processor)
        print(f"  - {table_name}: {processor_name}")
    
    print(f"\n总计: {len(processors)} 个处理器")

def test_custom_processor():
    """测试自定义处理器"""
    print("\n=== 测试自定义处理器 ===")
    
    # 模拟设备表数据
    mock_equipment_records = [
        {
            'record_id': 'rec_equipment_001',
            'fields': {
                '设备名称': '温湿度传感器',
                '设备类型': '环境监测',
                '型号': 'TH-2000',
                '制造商': '智能农业科技',
                '安装日期': 1640995200000,  # 2022-01-01
                '状态': '正常运行',
                '位置': '鸡舍A区',
                '图片': []
            }
        }
    ]
    
    # 测试设备表处理器
    equipment_processor = feishu_service._get_table_processor('设备')
    if equipment_processor:
        result = equipment_processor(mock_equipment_records)
        print("设备表处理结果:")
        print(f"  设备名称: {result[0]['equipment_name']}")
        print(f"  设备类型: {result[0]['equipment_type']}")
        print(f"  状态: {result[0]['status']}")
        print("✓ 设备表处理器测试通过")
    else:
        print("✗ 设备表处理器未找到")

def unregister_example():
    """演示取消注册处理器"""
    print("\n=== 取消注册示例 ===")
    
    # 取消注册设备表处理器
    feishu_service.unregister_table_processor('设备')
    print("✓ 已取消注册设备表处理器")
    
    # 检查是否还存在
    processor = feishu_service._get_table_processor('设备')
    if processor is None:
        print("✓ 确认设备表处理器已被移除")
    else:
        print("✗ 设备表处理器仍然存在")

def main():
    """主函数"""
    print("自定义数据表处理器示例")
    print("=" * 50)
    
    # 显示初始状态
    show_registered_processors()
    
    # 注册自定义处理器
    register_custom_processors()
    
    # 显示注册后的状态
    show_registered_processors()
    
    # 测试自定义处理器
    test_custom_processor()
    
    # 演示取消注册
    unregister_example()
    
    # 显示最终状态
    show_registered_processors()
    
    print("\n🎉 示例演示完成！")

if __name__ == "__main__":
    main()
