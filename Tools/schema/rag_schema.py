from langchain.pydantic_v1 import BaseModel, Field,Extra
from typing import Literal


class RagTool(BaseModel, extra=Extra.allow):
    query: str = Field(description="original `user input`")
    
class KGTool(BaseModel):
    query: str = Field(description="original `user input`")