# from pydantic import BaseModel, Field, Extra
from langchain.pydantic_v1 import BaseModel, Field, Extra
from typing import List



class AdvanceRagEnsemble(BaseModel, extra=Extra.allow) : 
    user_query:str=Field(description="original `user input`") 