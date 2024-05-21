from celery import Celery
from redis import Redis
from dataclasses import asdict

from DataIngestion.utils import pdf_utils,model_utils,mongo_utils, advanced_rag_utils,url_utils
from _temp.config import CeleryQueue,RedisBroker,AzureDocumentInfo,EMBEDDING,UseCaseMongo,PERSISTANT_DRIVE, ChromaClient, OpenAIConfig

from celery.utils.log import get_task_logger

import logging
import datetime
 
# Create and configure logger
logging.basicConfig(filename="logs/Celery.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
 
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

redis = Redis(**asdict(RedisBroker()))
redis.flushall()
redis.flushdb()

#BrokerUrl='pyamqp://guest:guest@20.41.249.147//'
#app = Celery(name='celery_queue',broker=BrokerUrl)
app=Celery(**asdict(CeleryQueue()))
#app = Celery('celery_queue', broker='redis://redis/0', backend='redis://redis/0')


# azure_form= model_utils.AzureDocIntell(**asdict(AzureDocumentInfo()))
# vectorizer=model_utils.ConvertToVector(EMBEDDING,azure_form)

azure_form= model_utils.AzureDocIntell_WT(**asdict(AzureDocumentInfo()))
vectorizer=model_utils.ConvertToVector_WT(EMBEDDING,azure_form)
usecase=UseCaseMongo()

metadata_rich_doc_obj = advanced_rag_utils.MetaDataRichDocumentProcessor(
    embeddings=EMBEDDING, chroma_creds=ChromaClient(), 
    azure_doc_creds= AzureDocumentInfo(), azure_openai_creds = OpenAIConfig()
)

url_vectorizer = url_utils.ConvertURLtoVector(EMBEDDING)


@app.task
def uploadpdf(uid,file_path,file_name):
    
    mongo=mongo_utils.MongoConnect(uri=usecase.uri,db=usecase.db,collection=usecase.collection)
    status_mongo=mongo_utils.MongoIngestionStatus(uri=usecase.uri,db=usecase.db,collection=usecase.collection)
    start_time=str(datetime.datetime.now())
    
    status_mongo.set_status("PROCESSING",uid,{
        "doc_name":file_name,
        "start_time":start_time
    })
    
    logger.info(f"========Started Consumption of {uid}=========")
    # vectorizer.convert_to_vector(file_path,uid)
    meta_data = metadata_rich_doc_obj.process(file_path,uid)
    print(meta_data)
    
    logger.info(f"=========End Consumption of {uid}=========")
    print("UID",uid)
    # mongo.update_data_by_id(uid,{'data_sources':{
    #     "storage_name":PERSISTANT_DRIVE,
    #     "collection_name":uid
        
    # }})
    print(uid)
    mongo.add_meta_data(idx = uid, meta_data = meta_data)
    status_mongo.set_status("COMPLETED",uid,{
        "doc_name":file_name,
        "end_time":str(datetime.datetime.now())
    })
    #mongo.update_data_by_id(uid,{'ingestion_status':{
    #    "doc_name":"file_path",
    #    "status":"COMPLETED",
    #    "start_time": start_time,
    #    "end_time":str(datetime.datetime.now())

    #}})
    logger.info(f"Updated:::{uid}")

@app.task
def uploadurl(uid, url_path):
    """
    Task to upload and process a URL.

    Args:
        uid (str): Unique identifier for the document (collection name for document).
        url_path (str): URL to be processed.

    Returns:
        None
    """   
    mongo=mongo_utils.MongoConnect(uri=usecase.uri,db=usecase.db,collection=usecase.collection)
    status_mongo=mongo_utils.MongoIngestionStatus(uri=usecase.uri,db=usecase.db,collection=usecase.collection)
    start_time=str(datetime.datetime.now())
    
    status_mongo.set_status("PROCESSING",uid,{
        "doc_name":url_path,
        "start_time":start_time
    })
    
    logger.info(f"========Started Consumption of {uid}=========")

    try:
        url_vectorizer.convert_url_to_vector(url_path,uid)
        logger.info(f"=========End Consumption of {uid}=========")
        print("UID",uid)
        mongo.update_data_by_id(uid,{'data_sources':{
            "storage_name":PERSISTANT_DRIVE,
            "collection_name":uid
            
        }})
        status_mongo.set_status("COMPLETED",uid,{
            "doc_name": url_path,
            "end_time":str(datetime.datetime.now())
        })
        logger.info(f"Updated:::{uid}")
    except Exception as e:
        logger.error(f"Error processing {uid}: {e}")
        status_mongo.set_status("FAILED", uid, {"doc_name": url_path, "end_time": str(datetime.datetime.now()), "error": str(e)})