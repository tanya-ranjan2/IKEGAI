from langchain.pydantic_v1 import BaseModel, Field, Extra

class ForecastingUsingProphet(BaseModel, extra=Extra.allow) : 
    filter_data: list[tuple] = Field(description="filtered data from the text-to-sql tool")
    feature_parameters: dict = Field(description="Extracted feature parameters from the extractor") 
