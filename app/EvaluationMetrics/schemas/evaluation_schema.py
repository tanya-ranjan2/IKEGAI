from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class LLM_Intialization(BaseModel):
    usecase_id: str
    user_id: Optional[str] | None = None
    model_name: str
    retrieval_context: Optional[list]| None=None 
    context: Optional[list]| None=None
    ts: datetime = Field(default_factory=datetime.now)
    