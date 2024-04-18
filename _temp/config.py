from dataclasses import dataclass,asdict


PERSISTANT_DRIVE="VectorDB"
STORAGE_DRIVE="Files"

MONGO_URI = "mongodb+srv://ikegai:ikegai%40123456@cluster0.l2apier.mongodb.net"
EMBEDDING="intfloat/e5-base-v2"


@dataclass
class OpenAIConfig:
    api_key:str="312ff50d6d954023b8748232617327b6"
    azure_endpoint:str="https://openai-lh.openai.azure.com/"
    azure_deployment:str="test"
    api_version:str="2024-02-15-preview"
    
    

@dataclass
class AzureDocumentInfo:
    api_key:str='f8c8e2179f44484c872de1bd373c17c0'
    end_point:str='https://spendanalytics.cognitiveservices.azure.com/'
    
@dataclass
class ChromaClient:
    host:str="http://20.41.249.147:6062"
    port:int=8000


@dataclass
class CeleryQueue:
    name:str='celery_queue'
    broker:str='redis://20.41.249.147:6379/0'
    backend:str="redis://20.41.249.147:6379/1"
    
    
@dataclass
class RedisBroker:
    host:str="20.41.249.147"
    port:int=6379
    username:str="default"
    password:str="admin"
    db:int=0


@dataclass
class UseCaseMongo:
    uri = "mongodb+srv://ikegai:ikegai%40123456@cluster0.l2apier.mongodb.net"
    db='ikegai'
    collection='usecases'
    
