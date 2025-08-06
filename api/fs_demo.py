from baseopensdk import BaseClient, JSON
from baseopensdk.api.base.v1 import *
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

APP_TOKEN = os.environ['APP_TOKEN']
PERSONAL_BASE_TOKEN = os.environ['PERSONAL_BASE_TOKEN']
TABLE_ID = os.environ['TABLE_ID']

# 构建client
client: BaseClient = BaseClient.builder() \
    .app_token(APP_TOKEN) \
    .personal_base_token(PERSONAL_BASE_TOKEN) \
    .build()
    
# 构造请求对象
request = ListAppTableRecordRequest.builder() \
    .table_id(TABLE_ID) \
    .page_size(20) \
    .build()

# 发起请求
response = client.base.v1.app_table_record.list(request)

# 打印序列化数据
print(JSON.marshal(response.data, indent=4))