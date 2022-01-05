import string
from typing import Union
from fastapi.datastructures import UploadFile
from pydantic.fields import Undefined
from pydantic.networks import EmailStr
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import null
from starlette import status
from api import schemas
from api.core.file_io import get_meta_data_from_scv, read_csv_by_line, save_file_to_disk
from api.crud.prospect import ProspectCrud

from api.models import ProspectsFile, prospect_files, Prospect


class ProspectsFilesCrud:
    @classmethod
    def create_prospects_files(
        cls, db: Session, user_id: int, file: bytes
    ) -> Union[ProspectsFile, None]:
        prospects_file = ProspectsFile(
            fileAddress="", user_id=user_id, status=prospect_files.ImportStatus.pending
        )

        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)

        file_address = save_file_to_disk(file, prospects_file.id)
        csv_metadata = get_meta_data_from_scv(file_address)

        prospects_file.fileAddress = file_address
        prospects_file.preview = csv_metadata[1]  # json preview
        prospects_file.file_rows = csv_metadata[0]  # rows

        db.commit()
        db.refresh(prospects_file)

        return prospects_file

    @classmethod
    def get_prospects_file(cls, db: Session, prospects_file_id: int) -> ProspectsFile:

        db_prospects_file = (
            db.query(ProspectsFile)
            .filter(ProspectsFile.id == prospects_file_id)
            .first()
        )

        if db_prospects_file is None:
            return None

        return db_prospects_file

    @classmethod
    def start_import_process_in_background(
        cls,
        db: Session,
        prospects_file_id: int,
        user_id: int,
        options: schemas.ProspectsFilePersitRequest,
    ):
        print("\n STARTING start_import_process_in_background PROCESS \n")

        db_prospects_file = db.query(ProspectsFile).get(prospects_file_id)

        if db_prospects_file is None:
            raise Exception("Error finding prospectsFiles record: " + prospects_file_id)

        # Skip the first row if “has_headers” parameter is true.
        range_start = 1 if options.has_headers else 0
        total_index = db_prospects_file.file_rows
        total_data_rows = total_index - range_start
        print("TOTAL DATA ROWS IN FILE " + total_data_rows.__str__() + "\n")

        # save the actual number of data rows
        db_prospects_file.total_data_rows = total_data_rows
        db.commit()
        db.refresh(db_prospects_file)

        new_record_count = 0

        for i in range(range_start, total_index):
            raw_row: str = read_csv_by_line(i, db_prospects_file.fileAddress)

            # model row
            row: list = raw_row.split(",")

            # match
            matched_record = (
                db.query(Prospect)
                .filter(Prospect.email == row[options.email_index])
                .first()
            )

            # Overwrite existing prospects if “force” parameter is true
            if matched_record is not None and options.force:
                print("RECORD MATCHED: " + matched_record.id.__str__())

                diffs = 0
                if row[options.email_index] != matched_record.email:
                    matched_record.email = row[options.email_index]
                    diffs += 1
                if row[options.first_name_index] != matched_record.first_name:
                    matched_record.first_name = row[options.first_name_index]
                    diffs += 1
                if row[options.last_name_index] != matched_record.last_name:
                    matched_record.last_name = row[options.last_name_index]
                    diffs += 1

                if diffs > 0:
                    print("DIFFS FOUND, UPDATING")
                    db.commit()
                else:
                    print("NO DIFFS FOUND, SKIPPING UPDATE")

            # if no match, create
            if matched_record is None:
                print("NO RECORD MATCHED, CREATING NEW RECORD")

                prospect = Prospect(
                    email=EmailStr(row[options.email_index]),
                    first_name=row[options.first_name_index],
                    last_name=row[options.last_name_index],
                    user_id=user_id,
                )
                db.add(prospect)
                db.commit()
                new_record_count += 1

                # save how many prospects are inserted from this CSV file
                db_prospects_file.done = new_record_count
                db.commit()
