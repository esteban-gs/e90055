from fastapi.datastructures import UploadFile
from fastapi import HTTPException, status, BackgroundTasks
from fastapi.param_functions import Depends
from fastapi.params import File
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import null

from api import schemas
from api.core.file_io import (
    get_csv_row_count_in_mem,
    get_file_size_in_mb_in_mem,
    get_meta_data_from_csv,
)
from api.crud.prospects_files import ProspectsFilesCrud
from api.schemas.prospect_files import (
    ProspectsFile,
    ProspectsFileCreateResponse,
    ProspectsFileImportStatusResponse,
)
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user

from string import Template


router = APIRouter(prefix="/api", tags=["prospects_files"])


@router.post("/prospects-files/", response_model=schemas.ProspectsFileCreateResponse)
async def create_prospects_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a csv file"
        )

    MAX_FILE_SIZE_MB = 200
    file_mb_size = None
    try:
        file_mb_size = get_file_size_in_mb_in_mem(file)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to read file",
        )
    is_valid_file_mb_size = file_mb_size <= MAX_FILE_SIZE_MB

    if not is_valid_file_mb_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum File Size of 200 MB Reached",
        )

    # validate file rows
    MAX_FILE_ROWS = 1000000
    number_of_file_rows = get_csv_row_count_in_mem(file)
    is_valid_file_rows = number_of_file_rows <= MAX_FILE_ROWS

    if not is_valid_file_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum NUMBER OF 1 MILLION ROWS EXCEEED",
        )

    new_record = ProspectsFilesCrud.create_prospects_files(
        db, current_user.id, file.file
    )

    return ProspectsFileCreateResponse(
        id=new_record.id,
        preview=get_meta_data_from_csv(new_record.file_address).preview,
    )


@router.post(
    "/prospects-files/{prospects_file_id}/prospects",
    response_model=schemas.ProspectsFile,
)
def persist_prospects_files(
    data: schemas.ProspectsFilePersitRequest,
    prospects_file_id: str,
    background_tasks: BackgroundTasks,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    # get db record
    db_prospects_file = ProspectsFilesCrud.get_prospects_file(db, prospects_file_id)

    if db_prospects_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
        )
    # set configuration based on the request -> pass to crud
    background_tasks.add_task(
        ProspectsFilesCrud.start_import_process_in_background,
        db,
        prospects_file_id=prospects_file_id,
        user_id=current_user.id,
        options=data,
    )

    return ProspectsFile(
        id=db_prospects_file.id,
        created_at=db_prospects_file.created_at,
        updated_at=db_prospects_file.updated_at,
        file_address=db_prospects_file.file_address,
    )


@router.get(
    "/prospects-files/{prospects_file_id}/progress",
    response_model=schemas.ProspectsFileImportStatusResponse,
)
def progress_status(
    prospects_file_id,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    # get db record
    db_prospects_file = ProspectsFilesCrud.get_prospects_file(db, prospects_file_id)

    done = ProspectsFilesCrud.get_import_progress_for(db, prospects_file_id)

    if db_prospects_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
        )

    return ProspectsFileImportStatusResponse(
        total=db_prospects_file.total_data_rows, done=done
    )
