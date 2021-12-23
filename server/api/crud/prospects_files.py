from typing import Union
from fastapi.datastructures import UploadFile
from sqlalchemy.orm.session import Session
from api.core.file_io import csv_to_json, save_file_to_disk

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
            user_id=user_id
        )

        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)

        file_address = save_file_to_disk(file, prospects_file.id)
        json_to_save = csv_to_json(file, 10, file_address)

        prospects_file.fileAddress = file_address
        prospects_file.preview = json_to_save

        db.commit()
        db.refresh(prospects_file)

        return prospects_file
