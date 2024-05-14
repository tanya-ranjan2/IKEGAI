from dataclasses import dataclass,asdict

###################ENV-SET######################
ENV="DEV"

# IF someone adds UAT just add UAT Env
if ENV=="PROD":
    URI="20.41.249.147"
    API_GET_DETAILS_FULL="https://ikegai.southindia.cloudapp.azure.com/solution-manager/v1/useCase/usecase-by-id?id={uid}"
    API_GET_DETAILS_PARTIAL="https://ikegai.southindia.cloudapp.azure.com/solution-manager/v1/useCase/?id={uid}"
elif ENV=="DEV":
    URI="52.172.103.119"
    API_GET_DETAILS_FULL="https://ikegai-dev.southindia.cloudapp.azure.com/solution-manager/v1/useCase/usecase-by-id?id={uid}"
    API_GET_DETAILS_PARTIAL="https://ikegai-dev.southindia.cloudapp.azure.com/solution-manager/v1/useCase/?id={uid}"

#################################
PERSISTANT_DRIVE="VectorDB"
STORAGE_DRIVE="Files"
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
    host:str=f"http://{URI}:6062"
    #host:str="http://192.168.1.2:6062"
    #port:int=6062


@dataclass
class CeleryQueue:
    name:str='celery_queue'
    broker:str=f'redis://{URI}:6379/0'
    backend:str=f"redis://{URI}:6379/1"
    
    
@dataclass
class RedisBroker:
    host:str=f'{URI}'
    #host:str="127.0.0.1"
    port:int=6379
    username:str="default"
    password:str="admin"
    db:int=0


@dataclass
class UseCaseMongo:
    uri = "mongodb+srv://ikegai:ikegai%40123456@cluster0.l2apier.mongodb.net"
    
    collection='usecases'
    if ENV=="PROD":
        db='ikegai'
    else:
        db='ikegai_dev'
    
