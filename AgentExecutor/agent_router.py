from fastapi import APIRouter
from AgentExecutor.schema import agent_schema
from AgentExecutor.src import agents,crew
from AgentExecutor.utils import helper

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
    llm=llmops.llmbuilder("azureopenai")
    rag_agent=helper.create_agents(config_data)[0]
    out,metadata=rag_agent._execute_agent(agent_info.query)
    return {"output":out,"metadata":metadata}


@router.post("/excute/")
def execute(agent_info:agent_schema.AgentExecute):
    config_data=APIconnector.get_usecase_details(agent_info.uid)
    llm=llmops.llmbuilder("azureopenai")
    agents_all=helper.create_agents(config_data)
    agent_crew=crew.Crew(agents=agents_all,llm=llm,)
    out,metadata=agent_crew.run(agent_info.query)
    return {"output":out,"metadata":metadata}
