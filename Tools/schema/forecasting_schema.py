from langchain.pydantic_v1 import BaseModel, Field, Extra

class ForecastingUsingProphet(BaseModel, extra=Extra.allow) : 
    user_query: str = Field(description="original `user input`") 
    mongo_store: bool = Field(description="to define if you want to push into the mongoDB")
    default_days: int = Field(description = "minimum days to forecast")
    db_path: str = Field(description = "path of the database for sql query")