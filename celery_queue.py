from celery import Celery
from redis import Redis
from dataclasses import asdict

from DataIngestion.utils import pdf_utils,model_utils,mongo_utils
from _temp.config import CeleryQueue,RedisBroker,AzureDocumentInfo,EMBEDDING,UseCaseMongo,PERSISTANT_DRIVE

redis = Redis(**asdict(RedisBroker()))

app = Celery(**asdict(CeleryQueue()))


azure_form= model_utils.AzureDocIntell(**asdict(AzureDocumentInfo()))
vectorizer=model_utils.ConvertToVector(EMBEDDING,azure_form)
usecase=UseCaseMongo()
mongo=mongo_utils.MongoConnect(uri=usecase.uri,db=usecase.db,collection=usecase.collection)

@app.task
def uploadpdf(uid,file_path):
    vectorizer.convert_to_vector(file_path,uid)
    mongo.update_data_by_id(uid,{'data_sources':{
        "storage_name":PERSISTANT_DRIVE,
        "collection_name":uid
        
    }})