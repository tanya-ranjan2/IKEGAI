from pymongo import MongoClient
from _temp.config import PERSISTANT_DRIVE



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
    '''
    def add_meta_data(self, idx, meta_data) : 
        # check if vectorDB exists as a key or not 
        try : 
            existing_vdb = self.collection.find_one({'id' : idx})['data_sources']['vectorDB'] 
            storage_name = self.collection.find_one({'id' : idx})['data_sources']['vectorDB'][0]["storage_name"] 
        except :
            if 'storage_name' in self.collection.find_one({'id' : idx})['data_sources'] :
                existing_vdb = [{
                    "storage_name" : self.collection.find_one({'id' : idx})['data_sources']["storage_name"], 
                    "collection_name"  : self.collection.find_one({'id' : idx})['data_sources']["collection_name"]
                }]
                storage_name = self.collection.find_one({'id' : idx})['data_sources']["storage_name"]
            else :
                existing_vdb, storage_name = [], PERSISTANT_DRIVE

        # check if meta_data exists as a key or not 
        try : 
            existing_meta_data = self.collection.find_one({'id' : idx})['data_sources']['meta_data']
        except : 
            existing_meta_data = []


        # insert into vectorDB key 
        existing_vdb.append(
            {"storage_name" : storage_name, "collection_name" : meta_data[0]["collection_name"]}
        )


        # insert into meta_data key 
        if existing_meta_data :
            existing_meta_data.append(meta_data[0])
        else : 
            existing_meta_data = meta_data

        # create the new doc 
        new_doc = {
            "vectorDB" : existing_vdb, "meta_data" : existing_meta_data
        }

        print("new doc to replace", new_doc)

        # replace with the new_doc 
        try :
            update_result = self.collection.update_one(
                {'id' : idx}, 
                {
                    "$set" : {
                        "data_sources" : new_doc
                    }
                }
            )

            print("modified count --> ", update_result.modified_count)

            return True 
        except : 
            return False 
    '''
    def add_meta_data(self, idx, meta_data,storage_name) :
        record=self.collection.find_one({'id' : idx})
        push2db={}
        if "data_sources" not in record:
            push2db["data_sources"]={}
        else:
            push2db["data_sources"]=record["data_sources"]
            
        if "vectorDB" not in record["data_sources"]:
            push2db["data_sources"]["vectorDB"]=[]
        else:
            push2db["data_sources"]["vectorDB"]=record["data_sources"]["vectorDB"]
            
        if "meta_data" not in record["data_sources"]:
            push2db["data_sources"]["meta_data"]=[]
        else:
            push2db["data_sources"]["meta_data"]=record["data_sources"]["meta_data"]
            

        push2db["data_sources"]["vectorDB"].append({"storage_name" : storage_name, "collection_name" : meta_data[0]["collection_name"]})
        push2db["data_sources"]["meta_data"].append(meta_data[0])
        try :
            update_result = self.collection.update_one(
                {'id' : idx}, 
                {
                    "$set" :push2db
                }
            )

            print("modified count --> ", update_result.modified_count)

            return True 
        except : 
            return False 
            
            
        
    def get_meta_data(self, idx) : 
        return self.collection.find_one({'id' : idx})['data_sources']['meta_data']
    
    def get_meta_data_without_id(self) : 
        output = []
        for usecase in self.collection.find() : 
            try : 
                output += usecase['data_sources']['meta_data']
            except : 
                pass 
        return output

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
        