import logging
from typing import Union
from pydantic.networks import EmailStr
from sqlalchemy.orm.session import Session
from api import schemas
from api.core.file_io import read_csv_by_line, save_file_to_disk, get_meta_data_from_csv
from api.crud.prospect import ProspectCrud

from api.models import ProspectsFile, prospect_files, Prospect


class ProspectsFilesCrud:
    @classmethod
    def create_prospects_files(
        cls, db: Session, user_id: int, file: bytes
    ) -> Union[ProspectsFile, None]:
        prospects_file = ProspectsFile(
            file_address="", user_id=user_id, status=prospect_files.ImportStatus.pending
        )

        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)

        file_address = save_file_to_disk(file, prospects_file.id)
        csv_metadata = get_meta_data_from_csv(file_address)

        prospects_file.file_address = file_address
        prospects_file.file_rows = csv_metadata.rows

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
        logging.info("BACKGROUND TASK STARTED")
        db_prospects_file = db.query(ProspectsFile).get(prospects_file_id)

        if db_prospects_file is None:
            raise Exception("Error finding prospectsFiles record: " + prospects_file_id)

        # Skip the first row if “has_headers” parameter is true.
        range_start = 1 if options.has_headers else 0
        total_index = db_prospects_file.file_rows
        total_data_rows = total_index - range_start

        # save the actual number of data rows
        db_prospects_file.total_data_rows = total_data_rows
        db.commit()
        db.refresh(db_prospects_file)

        for i in range(range_start, total_index):
            raw_row: str = read_csv_by_line(i, db_prospects_file.file_address)

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
                    matched_record.prospects_file_id = prospects_file_id
                    db.commit()

            # if no match, create, but only when email validates, otherwise skip the row
            if matched_record is None:
                try:
                    email_to_save = EmailStr.validate(row[options.email_index])
                except Exception as e:
                    logging.debug(e)
                    logging.debug(
                        "skipping invalid row with email: " + row[options.email_index]
                    )
                else:
                    prospect = Prospect(
                        email=email_to_save,
                        first_name=row[options.first_name_index],
                        last_name=row[options.last_name_index],
                        user_id=user_id,
                        prospects_file_id=prospects_file_id,
                    )
                    db.add(prospect)
                    db.commit()

        db_prospects_file.status = prospect_files.ImportStatus.complete
        db.commit()
        logging.info("BACKGROUND TASK ENDED")

    @classmethod
    def get_import_progress_for(cls, db: Session, prospects_file_id: int) -> int:
        total_imported = (
            db.query(Prospect)
            .filter(Prospect.prospects_file_id == prospects_file_id)
            .count()
        )
        return 0 if total_imported == None else total_imported
