from fastapi import APIRouter
from AgentExecutor.schema import agent_schema
from AgentExecutor.src import agents,crew
from AgentExecutor.utils import helper
import requests

#<CODEBLOCk>
import json
from utils import parser,llmops,APIconnector

#<CODEBLOCk>
router=APIRouter(prefix='/agent',tags=["agent_execution"])




@router.get("/get_details/{uid}")
def get_agent_details(uid):
    
    return {"uid":uid}

@router.post("/execute_agent/")
def execute_agent(agent_info:agent_schema.AgentExecute):
    config_data=APIconnector.get_usecase_details(agent_info.uid)
    print("CONFIG",config_data)
    if 'is_direct_api' in config_data:
        print("API_URL",config_data['api_url'])
        if config_data['is_direct_api']:
            res=requests.post(url=config_data['api_url'],json={"uid":agent_info.uid,"query":agent_info.query},headers={"content-type":"application/json"})
            if res.status_code==200:
                return res.json()
            else:
                return {"status":404}
    llm=llmops.llmbuilder("azureopenai")
    agents=helper.create_agents(config_data)
    if len(agents)==1:
        agent=helper.create_agents(config_data)[0]
        out,metadata,followup=agent._execute_agent(agent_info.query)
        
    else:
        agent_crew=crew.Crew(agents=agents,llm=llm,)
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
