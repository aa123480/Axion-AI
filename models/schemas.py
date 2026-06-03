#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

from typing_extensions import Literal

from pydantic.v1 import BaseModel

#----------------------------------------------------------------------------------#
# Models and Schemas
#----------------------------------------------------------------------------------#

class Stats(BaseModel):
    kills : int
    deaths: int
    accuracy: float

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]