import os
import string
import linecache
from shutil import copyfileobj
from fastapi.datastructures import UploadFile

import csv
import json


def save_file_to_disk(file: bytes, file_id: int) -> string:
    file_name = '{}.csv'.format(file_id)

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


def get_meta_data_from_scv(file_location, headings: bool = True) -> list:
    preview: list = []

    with open(file_location, encoding='utf-8') as csvf:
        csvReader = csv.reader(csvf)
        counter = 0
        for row in csvReader:
            if row.__len__ != 0: # skip empty rows, plz
                print("raw row")
                print(row)
                counter += 1

            if counter < 10: # preview only
                nested = []
                for word in row:
                    nested.append(word)
                preview.append(nested)
        print(counter)
    return [counter, preview]


def read_csv_by_line(index: int, file_path) -> str:
    return linecache.getline(file_path, index + 1).rstrip()
