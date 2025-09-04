import requests

url = "https://base-api.feishu.cn/open-apis/bitable/v1/apps/GXrdbXWcNauYK8s5zdEcK73Snbd/tables"

payload={}
headers = {
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Authorization': 'Bearer pt-Z924DLNmOGFWxHCK8O0emjDLz4Bf9TKxaG9ZtmiZAQAAAUBIFgJAxPSSuE4I'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)