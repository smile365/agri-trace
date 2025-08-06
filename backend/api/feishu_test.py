import requests

host = 'https://base-api.feishu.cn'

def list_tables(app_token,user_token):
    list_table_url = f'{host}/open-apis/bitable/v1/apps/{app_token}/tables'
    headers = {
    'Authorization': 'Bearer %s' % user_token
    }
    response = requests.request("GET", list_table_url, headers=headers)
    print(response.text)


def list_records(app_token,table_id,user_token):
    list_record_url = f'{host}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'
    headers = {
    'Authorization': 'Bearer %s' % user_token
    }
    response = requests.request("GET", list_record_url, headers=headers)
    print(response.text)


if __name__ == '__main__':
    app_token = 'KnOFbTu1harM6wsNbWdcro2Rnoc'
    user_token = 'pt-eHTfXM5N-Z_DP5H4UdggH4sjyPpfe-2cYHO0kmiYAQAAHABAsAKAC47s_BN9'
    table_id = 'tblELkotV4rh2PCz'
    list_records(app_token,table_id,user_token)
