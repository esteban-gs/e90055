from typing import Union
from fastapi.datastructures import UploadFile
from pydantic.fields import Undefined
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import null
from starlette import status
from api.core.file_io import get_json_from_scv, save_file_to_disk

from api.models import ProspectsFile, prospect_files


class ProspectsFilesCrud:
    @classmethod
    def create_prospects_files(
            cls,
            db: Session,
            user_id: int,
            file: UploadFile) -> Union[ProspectsFile, None]:
        prospects_file = ProspectsFile(
            fileAddress="",
            user_id=user_id,
            status=prospect_files.ImportStatus.pending
        )

        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)

        file_address = save_file_to_disk(file, prospects_file.id)
        json_to_save = get_json_from_scv(False, file_address)

        prospects_file.fileAddress = file_address
        prospects_file.preview = json_to_save

        db.commit()
        db.refresh(prospects_file)

        return prospects_file

    @classmethod
    def get_prospects_file(
        cls,
        db: Session,
        prospects_file_id: int
    ) -> ProspectsFile:

        db_prospects_file = db.query(ProspectsFile)\
            .filter(ProspectsFile.id == prospects_file_id)\
            .first()

        if db_prospects_file is None:
            return None

        return db_prospects_file
