import os
import string
import linecache
from shutil import copyfileobj
from fastapi.datastructures import UploadFile

import csv
import json

from api.schemas.prospect_files import ProspectsFilePreview


def save_file_to_disk(file: bytes, file_id: int) -> string:
    file_name = "{}.csv".format(file_id)

    dir_save_path = os.path.join("files")

    file_save_path = os.path.join(dir_save_path, file_name)

    if not os.path.exists(dir_save_path):
        os.mkdir(dir_save_path)

    with open(file_save_path, "wb+") as out_file:
        copyfileobj(file, out_file)  # write in chunks

    # is files wasn't saved something went wrong
    if not os.path.exists(file_save_path):
        raise Exception("File was not saved correctly")
    return file_save_path


def get_meta_data_from_csv(file_location) -> ProspectsFilePreview:
    PREVIEW_LIMIT = 10
    preview: list = []

    with open(file_location, encoding="utf-8") as csvf:
        csvReader = csv.reader(csvf)
        rows = 0
        for row in csvReader:
            if row.__len__ != 0:  # skip empty rows, plz
                rows += 1

            if rows < PREVIEW_LIMIT:  # preview only
                nested = []
                for word in row:
                    nested.append(word)
                preview.append(nested)
    return ProspectsFilePreview(rows=rows, preview=preview)


def read_csv_by_line(index: int, file_path) -> str:
    return linecache.getline(file_path, index + 1).rstrip()


def get_file_size_in_mb_in_mem(file: UploadFile) -> int:
    # when reading a file multiple times, returning the byte pointer to 0 is required
    # https://stackoverflow.com/a/28320785/13862254

    # validate file size in MB
    BYTE_TO_MB_RATIO = 1000000
    file_in_mem_length = None
    try:
        file_in_mem_length = file.file.seek(0, os.SEEK_END)
        file.file.seek(0, 0)
    except:
        raise Exception("Unable to read file")
    return file_in_mem_length.__sizeof__() / BYTE_TO_MB_RATIO


def get_csv_row_count_in_mem(file: UploadFile) -> int:
    MAX_FILE_ROWS = 1000000
    number_of_file_rows = len(file.file.readlines())
    file.file.seek(0, 0)
    return number_of_file_rows
