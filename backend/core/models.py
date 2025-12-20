#defining the pydantic models needed to load in the LLM data
#it tells the LLM what all to give in the answer and in what way

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StoryOptionLLM(BaseModel):
    text: str = Field(description="the text of the option shown to the user")
    nextNode: Dict[str, Any] = Field(description="the next node content and its options")

class StoryNodeLLM(BaseModel):
    content: str = Field(description="the main content of the story node")
    isEnding: bool = Field(description="whether the story is ending node")
    isWinningEnding: bool = Field(description="whether the story is winning ending node")
    options: Optional[List[StoryOptionLLM]] = Field(default=None, description="the story options for this node")

class StoryLLMResponse(BaseModel):
    title: str = Field(description="the title of the story")
    rootNode: StoryNodeLLM = Field(description="the root node of the story")
