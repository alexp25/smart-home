import json
import appVariables
import pymongo
from bson import json_util


class MongoManager(object):
    def __init__(self):
        self.conn=None

    def connect(self):
        try:
            self.conn = pymongo.MongoClient('mongodb://localhost:27017/')
            msg = "[MongoManager] Connected successfully"
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)
        except pymongo.errors.ConnectionFailure, e:
            msg = "[MongoManager] Could not connect to MongoDB: " + e
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

    def find(self,db,collection,query):
        if query is None:
            result = self.conn[db][collection].find()
        else:
            result = self.conn[db][collection].find(query)
        result_list = list(result)
        # msg = json.dumps(result_list, default=json_util.default, indent=2)
        # if not appVariables.qDebug1.full():
        #     appVariables.qDebug1.put(msg)
        return result_list
        # return json.dumps(result_list, default=json_util.default, indent=2)
        # print(result_list)
        # # print(result_list[0]['key'])
        # print(json.dumps(result_list, default=json_util.default, indent=2))
    def find_last_records(self,db,collection,query,N):
        if N!=0:
            pipeline=[{"$match": query},
                      { "$sort" : { "_id" : -1 }},
                      { "$limit" : N },
                      { "$sort" : { "_id" : 1 }}
                      ]
        else:
            pipeline = [{"$match": query},
                        {"$sort": {"_id": 1}}
                        ]
        result = self.conn[db][collection].aggregate(pipeline)
        # if query is None:
        #     result = self.conn[db][collection].find({}).limit(N).sort([("_id",-1),])
        # else:
        #     result = self.conn[db][collection].find(query).limit(N).sort([("_id",-1),])
        result_list = list(result)
        return result_list
        # db.sensor_data.find({"s_id": 132}).limit(3).sort({_id: -1})



    def insert(self,db,collection,document):
        result = self.conn[db][collection].insert(document)
        return result

    def update(self,db,collection,query,update_doc,ups=False):
        result = self.conn[db][collection].update(query, update_doc, upsert=ups)
        return result

    def remove(self,db,collection,document):
        result = self.conn[db][collection].remove(document)
        return result

    def aggregate_pipeline(self,db,collection,pipeline):
        result = self.conn[db][collection].aggregate(pipeline)
        result_list = list(result)
        return result_list


