#defining what type of data the API accepts and returns, allows API to do data validation
#giving the structure of data to pydantic for automatic validation

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class StoryOptionsSchema(BaseModel):
    text:str
    node_id: Optional[int] = None

class StoryNodeBase(BaseModel): #used as a parent class to make things simpler when writing more schemas
    content:str
    is_ending: bool = False
    is_winning_ending: bool = False

class CompleteStoryNodeResponse(StoryNodeBase): #what the response to the frontend will be
    id: int
    options: List[StoryOptionsSchema] = []

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    session_id: Optional[str] = None

    class Config:
        from_attributes = True

class CreateStoryRequest(StoryBase): #what comes from the frontend to be sent to the API
    theme: str

class CompleteStoryResponse(StoryBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes = True
