import csv
import os
from fastapi.datastructures import UploadFile
from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from fastapi.params import File
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import null

from api import schemas
from api.crud.prospects_files import ProspectsFilesCrud
from api.schemas.prospect_files import ProspectsFileCreateResponse
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user

from string import Template


router = APIRouter(prefix="/api", tags=["prospects_files"])


@router.post("/prospects-files/", response_model=schemas.ProspectsFileCreateResponse)
def create_prospects_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a csv file"
        )

    # needs to be created first to ge the
    new_record = ProspectsFilesCrud.create_prospects_files(
        db, current_user.id, file)

    return ProspectsFileCreateResponse(
        id=new_record.id,
        preview=new_record.preview
    )


@router.post("/prospects-files/{file_id}/prospects")
def persist_prospects_files(
    data: schemas.ProspectsFilePersitRequest,
    file_id: str,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # get db record
    db_prospects_file = ProspectsFilesCrud.get_prospects_file(db, file_id)

    if db_prospects_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
        )
    # set configuration based on the request -> pass to core
    

    # match, then update, create

    return db_prospects_file
