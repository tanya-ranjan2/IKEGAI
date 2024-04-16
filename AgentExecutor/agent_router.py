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
            
    if agent_info.session_id in session.sessions:
        agent=session.sessions[agent_info.session_id]['obj']
        if session.sessions[agent_info.session_id]['type']=='agent':
            out,metadata,followup=agent._execute_agent(agent_info.query)
        else:
            out,metadata,followup=agent.run(agent_info.query)
    else:
        llm=llmops.llmbuilder("azureopenai")
        agents=helper.create_agents(config_data)
        if len(agents)==1:
            agent=helper.create_agents(config_data)[0]
            session.sessions[agent_info.session_id]={
                "type":'agent',
                "obj":agent
            }
            out,metadata,followup=agent._execute_agent(agent_info.query)
            
        else:
            agent_crew=crew.Crew(agents=agents,llm=llm,)
            session.sessions[agent_info.session_id]={
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
async def create_upload_file(file: UploadFile,idx:str):
    
    contents = file.file.read()
    with open(os.path.join(STORAGE_DRIVE,file.filename), 'wb') as f:
        f.write(contents)
    uploadpdf.delay(idx,os.path.join(STORAGE_DRIVE,file.filename))
    return {"filename": file.filename}