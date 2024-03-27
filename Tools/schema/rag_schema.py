from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal

class MergeTool(BaseModel):
    query: str = Field(description="original `user input`")
    #llm: Literal['azureopenai','hugginface'] = Field(description="LLM function to be called")
    llm:str = Field(description="LLM function to be called")
    prev_tools: list= Field(description="List of previous tools")
    intermediatory_steps: dict= Field(description="All previous steps taken by other tools")
        
class RagTool(BaseModel):
    query: str = Field(description="original `user input`")
    storage_name: str = Field(description="Name of the vector database to be Searched")

class KGTool(BaseModel):
    query: str = Field(description="original `user input`")