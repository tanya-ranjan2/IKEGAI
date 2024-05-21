from pydantic import BaseModel, Field
from typing import List,Literal

class RerankingSchema(BaseModel):
    rating:int=Field(description="Rating for context and question between 1 to 5")
    reasoning:str=Field(description="Reasoning for the scoring")