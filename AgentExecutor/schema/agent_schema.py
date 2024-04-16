from pydantic import BaseModel


class AgentID(BaseModel):
    uid:str
    
    
class AgentExecute(BaseModel):
    uid:str
    query:str
    session_id:str