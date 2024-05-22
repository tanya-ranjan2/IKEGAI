from pydantic import BaseModel, Field
from typing import List,Literal

class MetaDataOfDocuments(BaseModel):
    organization:str=Field(description="Name of the organization about which the Document is about")
    period:str=Field(description="Time frame or Date given")
    subject:str=Field(description="Brief about the document")
    topics:List[str]=Field(default_factory=list, description="Topics covered by the document. Examples include Computer Science, Biology, Chemistry, etc.")

class RerankingSchema(BaseModel):
    rating:int=Field(description="Rating for context and question between 1 to 5")
    reasoning:str=Field(description="Reasoning for the scoring")