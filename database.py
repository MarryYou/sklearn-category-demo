import pymongo
class DataBaseClient:
    def __init__(self,host,port):
        #传入主机名，port端口
        self.host = host
        self.port = port
        self.client  = pymongo.MongoClient(host=self.host,port=self.port) #定义客户端
    def setDB(self,Dname):#设置选择的DB
        try:
            self.db = self.client[Dname]
            return self.db
        except Exception as e:
            print(e)

    def setCollection(self, Cname):  # 设置选择的collection
        try:
            self.collection = self.db[Cname]
            return self.collection
        except Exception as e:
            print(e)
    def delete_one(self,data):
        try:  # 删除单条 传入dict
            self.collection.delete_one(data)
        except Exception as e:
            print(e)
    def delete_many(self,data):
        try:  # 删除多条 传入list
            self.collection.delete_many(data)
        except Exception as e:
            print(e)
    def add_many(self, data):  # 插入多条 传入list
        try:
            self.collection.insert_many(data)
        except Exception as e:
            print(e)
    def add_one(self, data):  # 单条插入,传入dict
        try:
            self.collection.insert_one(data)
        except Exception as e:
            print(e)
    def get_many(self, info):  # 这里是查询多条,标准格式，自行百度
        try:
            doc_list = []
            for item in self.collection.find(info):
                doc_list.append(item)
            return doc_list
        except Exception as e:
            print(e)
    def update_one(self,data,updateitem):
        try:  # 这里是更新单个,标准格式，自行百度
            self.collection.update_one(data,updateitem)
        except Exception as e:
            print(e)
    def get_one(self, info):
        try:  # 这里是查询单个,标准格式，自行百度
            doc = self.collection.find_one(info)
            return doc
        except Exception as e:
            print(e)
