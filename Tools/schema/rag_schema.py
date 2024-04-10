from langchain.pydantic_v1 import BaseModel, Field,Extra
from typing import Literal


class RagTool(BaseModel, extra=Extra.allow):
    query: str = Field(description="original `user input`")
    topk: int = Field(default=3,description="No of document chunks to retrived. By default it is 3.")
    llm:Literal["AzureOpenAI","Hugginface"]=Field(description="Name of LLM")
    
class KGTool(BaseModel):
    query: str = Field(description="original `user input`")