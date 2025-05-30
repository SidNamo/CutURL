from pydantic import BaseModel

class CutRequest(BaseModel):
    url: str

class DeleteRequest(BaseModel):
    uid: int

