from langchain.pydantic_v1 import BaseModel, Field, Extra

class ExtractKeywords(BaseModel, extra=Extra.allow) : 
    user_query: str = Field(description="original `user input`") 
    default_days: int = Field(description="minimum days to forecast")