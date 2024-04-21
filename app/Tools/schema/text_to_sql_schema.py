from langchain.pydantic_v1 import BaseModel, Field, Extra

class TextToSQL(BaseModel, extra=Extra.allow) :  
    user_query: str = Field(description="this is a user given query") 
