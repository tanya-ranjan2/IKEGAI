from fastapi import APIRouter
from AgentExectutor.schema import agent_schema
from AgentExectutor.src import agents
from Tools.src.rag.rag_tools import rag,kg_rag,mergetool
#<CODEBLOCk>
import json
from utils import parser,llmops

#<CODEBLOCk>
router=APIRouter(prefix='/agent',tags=["agent_execution"])


@router.post("/get_details/")
def get_agent_details(uid:agent_schema.AgentID):
    
    return {"uid":uid.uid}

@router.post("/execute/")
def execute(agent_info:agent_schema.AgentExecute):
    #<CODEBLOCk>
    #change it to search by ID and Execute
    llm=llmops.llmbuilder("azureopenai")
    config_data=json.load(open('_temp/configManager.json'))
    agent_details=parser.get_agent_details(config_data)
    #<CODEBLOCk>
    rag_agent= agents.Agent(
        role=agent_details[0]['role'],
        desc=agent_details[0]['desc'],
        llm=llm,
        tools=[rag,kg_rag,mergetool],
        config=agent_details[0]['func_config'],
        verbose=True
    )
    out=rag_agent._execute_agent(agent_info.query)
    return {"output":out}
