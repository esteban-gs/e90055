from datetime import datetime
from fastapi.datastructures import UploadFile
from pydantic import BaseModel


class ProspectsFile(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    fileAddress: str
    preview: dict  # 2D array representing first 10 rows

    class Config:
        orm_mode = True


# class ProspectFileCreate(BaseModel):
#     file: UploadFile

class ProspectFileCreateResponse(BaseModel):
    id: int
    preview: dict
