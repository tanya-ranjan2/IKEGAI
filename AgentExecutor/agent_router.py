from fastapi import APIRouter
from AgentExecutor.schema import agent_schema
from AgentExecutor.src import agents,crew
from AgentExecutor.utils import helper

#<CODEBLOCk>
import json
from utils import parser,llmops

#<CODEBLOCk>
router=APIRouter(prefix='/agent',tags=["agent_execution"])


@router.post("/get_details/")
def get_agent_details(uid:agent_schema.AgentID):
    
    return {"uid":uid.uid}

@router.post("/execute_agent/")
def execute_agent(agent_info:agent_schema.AgentExecute):
    #<CODEBLOCk>
    #change it to search by ID and Execute
    llm=llmops.llmbuilder("azureopenai")
    config_data=json.load(open('_temp/configManager.json'))
    agent_details=parser.get_agent_details(config_data)
    #<CODEBLOCk>
    rag_agent=helper.create_agents(config_data)[0]
    out=rag_agent._execute_agent(agent_info.query)
    return {"output":out}


@router.post("/excute/")
def execute(agent_info:agent_schema.AgentExecute):
    #<CODEBLOCk>
    #change it to search by ID and Execute
    config_data=json.load(open('_temp/configManager.json'))
    llm=llmops.llmbuilder("azureopenai")
     #<CODEBLOCk>
    agents_all=helper.create_agents(config_data)
    agent_crew=crew.Crew(agents=agents_all,llm=llm,)
    out=agent_crew.run(agent_info.query)
    return {"output":out}
'''
@router.post("/execute/{uid}")
def execute_uid(uid):
    #<CODEBLOCk>
    #change it to search by ID and Execute
    
    return {"output":uid}
'''