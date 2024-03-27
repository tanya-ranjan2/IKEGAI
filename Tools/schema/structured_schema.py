from langchain.pydantic_v1 import BaseModel, Field



class SQLGeneratorTool(BaseModel):
    query: str = Field(description="original `user input`")
    
    
class SQLExecutor(BaseModel):
    sql_query: str = Field(description="Generated SQL query")
    creds: dict = Field(description="Credentials of the SQL Database")