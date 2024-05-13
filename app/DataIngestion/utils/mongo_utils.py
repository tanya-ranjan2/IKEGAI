from pymongo import MongoClient




class MongoConnect:
    def __init__(self,uri,db,collection) -> None:
        self.client = MongoClient(uri)
        self.db=self.client[db]
        self.collection=self.db[collection]
        
    def get_data_by_id(self,idx):
        return self.collection.find_one({'id':idx})
    
    def get_data(self,filters):
        return [i for i in self.collection.find(filters)]
    
    def update_data_by_id(self,idx,record):
        try:
            self.collection.update_one({"id":idx},{'$set': record})
            return True
        except:
            return False

class MongoIngestionStatus(MongoConnect):
    
        
    def set_status(self,status,idx,info):
        if status=="QUEUED":
            self.collection.update_one(
                {"id":idx},
                {"$addToSet":{"ingestion_status":info}}
            )
        elif status=="PROCESSING":
            self.collection.update_one({"id":idx},{'$set':{
                    "ingestion_status.$[updateFriend].status" : status,
                    "ingestion_status.$[updateFriend].start_time" : info['start_time'],
                    
                    }},
                    array_filters=[
                    {"updateFriend.doc_name" : info["doc_name"]},
                    ]
                )
        elif status=="COMPLETED":
            self.collection.update_one({"id":idx},{'$set':{
                    "ingestion_status.$[updateFriend].status" : status,
                    "ingestion_status.$[updateFriend].end_time" : info['end_time'],
                    }},
                    array_filters=[
                    {"updateFriend.doc_name" : info["doc_name"]},
                    ]
                )
        