from datetime import datetime
from fastapi.datastructures import UploadFile
from pydantic import BaseModel


class ProspectsFile(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    fileAddress: str
    preview: list  # 2D array representing first 10 rows

    class Config:
        orm_mode = True


# class ProspectFileCreate(BaseModel):
#     file: UploadFile


class ProspectsFileCreateResponse(BaseModel):
    id: int
    preview: list


class ProspectsFileImportStatusResponse(BaseModel):
    total: int
    done: int


class ProspectsFilePersitRequest(BaseModel):
    email_index: int
    first_name_index: int
    last_name_index: int
    force: bool
    has_headers: bool
