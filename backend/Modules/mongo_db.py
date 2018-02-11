import json
import appVariables
import pymongo
from bson import json_util


class MongoManager(object):
    def __init__(self):
        self.conn=None

    def connect(self):
        result = False
        try:
            self.conn = pymongo.MongoClient('mongodb://localhost:27017/')
            msg = "[MongoManager] Connected successfully"
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)
            result = True
        except pymongo.errors.ConnectionFailure, e:
            msg = "[MongoManager] Could not connect to MongoDB: " + str(e)
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

        return result

    def find(self, db, collection, query):
        if self.conn:
            if query is None:
                result = self.conn[db][collection].find()
            else:
                result = self.conn[db][collection].find(query)
            result_list = list(result)
        else:
            result_list = None
        return result_list

    def find_last_records(self, db, collection, query, N):
        if self.conn:
            if query is None:
                result = self.conn[db][collection].find({}).sort([("_id",-1),]).limit(N)
            else:
                result = self.conn[db][collection].find(query).sort([("_id",-1),]).limit(N)
            result_list = list(result)
        else:
            result_list = None
        return result_list
        # db.sensor_data.find({"s_id": 132}).limit(3).sort({_id: -1})



    def insert(self,db,collection,document):
        if self.conn:
            result = self.conn[db][collection].insert(document)
        else:
            result = None
        return result

    def update(self,db,collection,query,update_doc,ups=False):
        if self.conn:
            result = self.conn[db][collection].update(query, update_doc, upsert=ups)
        else:
            result = None
        return result

    def remove(self,db,collection,document):
        if self.conn:
            result = self.conn[db][collection].remove(document)
        else:
            result = None
        return result

    def aggregate_pipeline(self,db,collection,pipeline):
        if self.conn:
            result = self.conn[db][collection].aggregate(pipeline)
            result_list = list(result)
        else:
            result_list = None
        return result_list


