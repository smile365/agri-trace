import json 

json_data = {'version': 'v1', 'messageId': '58736107831678119', 'rulechainId': 'rerau49a99d1sufq9qe1drigd1ykpejs', 'message': 'NTMuMCAyNi45', 'timestamp': 1754727137925, 'source': {'type': 'IOT_CORE', 'iotCoreId': 'adakqct', 'topic': 'WifiDHT/9C9C1F944799/DHT11', 'clientId': 'wifiDHT11-ID0x9C9C1F944799'}}


print(json.dumps(json_data, indent=4))
