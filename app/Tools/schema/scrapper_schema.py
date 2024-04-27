from langchain.pydantic_v1 import BaseModel, Field, Extra

class ScrapperTool(BaseModel, extra=Extra.allow):
    query: str = Field(description="original `user input`")
    url: str = Field(description="the url to be used for scraping information")