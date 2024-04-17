from fastapi import APIRouter
from AgentExecutor.schema import agent_schema
from AgentExecutor.src import agents,crew
from AgentExecutor.utils import helper,sessions
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
import requests
import json
import os

#<CODEBLOCk>
from utils import parser,llmops,APIconnector
from celery_queue import uploadpdf

from _temp.config import STORAGE_DRIVE

#<CODEBLOCk>
router=APIRouter(prefix='/agent',tags=["agent_execution"])

session=sessions.SessionData()


@router.get("/get_details/{uid}")
def get_agent_details(uid):
    
    return {"uid":uid}

@router.post("/execute_agent/")
def execute_agent(agent_info:agent_schema.AgentExecute):
    config_data=APIconnector.get_usecase_details(agent_info.uid)
    #print("CONFIG",config_data)
    if 'is_direct_api' in config_data and 'api_url' in config_data:
        #print("API_URL",config_data['api_url'])
        if config_data['is_direct_api']:
            res=requests.post(url=config_data['api_url'],json={"uid":agent_info.uid,"query":agent_info.query},headers={"content-type":"application/json"})
            if res.status_code==200:
                return res.json()
            else:
                return {"status":404}
    uuids=agent_info.session_id+agent_info.uid
    if uuids in session.sessions:
        agent=session.sessions[uuids]['obj']
        if session.sessions[uuids]['type']=='agent':
            print("Running Agent...",agent.chat_history)
            out,metadata,followup=agent._execute_agent(agent_info.query)
        else:
            out,metadata,followup=agent.run(agent_info.query)
    else:
        print("---------Builder--------")
        llm=llmops.llmbuilder("azureopenai")
        agents=helper.create_agents(config_data)
        if len(agents)==1:
            agent=helper.create_agents(config_data)[0]
            session.sessions[uuids]={
                "type":'agent',
                "obj":agent
            }
            out,metadata,followup=agent._execute_agent(agent_info.query)
            
        else:
            agent_crew=crew.Crew(agents=agents,llm=llm,)
            session.sessions[uuids]={
                "type":'crew',
                "obj":agent_crew
            }
            out,metadata,followup=agent_crew.run(agent_info.query)
    return {"output":out,"metadata":metadata,"followup":followup}


@router.post("/excute/")
def execute(agent_info:agent_schema.AgentExecute):
    config_data=APIconnector.get_usecase_details(agent_info.uid)
    llm=llmops.llmbuilder("azureopenai")
    agents_all=helper.create_agents(config_data)
    agent_crew=crew.Crew(agents=agents_all,llm=llm,)
    out,metadata=agent_crew.run(agent_info.query)
    return {"output":out,"metadata":metadata}


@router.post("/uploadfile/{idx}")
def create_upload_file(file: list[UploadFile],idx:str):
    files=[f for f in file]
    for file in files:
        contents = file.file.read()
        with open(os.path.join(STORAGE_DRIVE,file.filename), 'wb') as f:
            f.write(contents)
        uploadpdf.delay(idx,os.path.join(STORAGE_DRIVE,file.filename))
    return {"filename": [f.filename for f in files]}


@router.get("/download/{filename}")
async def dowload(filename:str):
    pdf_name_mapping={'az1742-2018.pdf':'Solar Photovoltic (PV) System Components.pdf',
                          '6981.pdf':"Photovoltics: Basic Design Princicals and Components.pdf",
                          'BOOK3.pdf':"Solar Photovoltics Technology and Systems.pdf"
                          }
    reverse_mapping={v:k for k,v in pdf_name_mapping.items()}
    if filename in reverse_mapping:
        filename=reverse_mapping[filename]
    file_path=os.path.join(STORAGE_DRIVE,filename)
    return FileResponse(path=file_path, filename=file_path, media_type='text/pdf')