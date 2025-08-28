class BDLotCache:
    '''
    百度智能云lot缓存
    '''

    def __init__(self):
        self.cache:Dict[str:str] = {}

    def __getkey__(self,url:str)->str:
        '''
        获取url的key,key是url的路径部分,不包含查询参数
        url: http://192.168.15.33:8080/api/v1/test/devices?qs=c05b4392ea4b5d4cd1464ef83
        return: test/devices
        '''
        key = url.split('?')[0].split('api/v1/')[1]
        return key

    def set(self,url:str, query_string:str)->str:
        if not query_string or len(query_string) <1 or not '=' in query_string:
            return
        key = self.__getkey__(url)
        value = query_string.split('&')[0].split('=')[1]
        if not value or len(value) < 2:
            return
        self.cache[key] = value
        print(f'key={key},value={value}')
        return value

    def get(self,url:str)->str:
        key = self.__getkey__(url)
        print(f'key={key}')
        if key in self.cache:
            return self.cache[key]
        return ''
    
    def setv(self,key:str,value:str):
        self.cache[key] = value
    
    def getv(self,key:str)->str:
        if key in self.cache:
            return self.cache[key]
        return None


bd_lot_cache = BDLotCache()

