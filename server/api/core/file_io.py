import os
import string
from fastapi.datastructures import UploadFile

import csv
import json


def save_file_to_disk(file: UploadFile, file_id: int) -> string:
    fileBytes = file.file.read()

    file_name = '{}.csv'.format(file_id)

    dir_save_path = os.path.join("files")

    file_save_path = os.path.join(dir_save_path, file_name)

    if not os.path.exists(dir_save_path):
        os.mkdir(dir_save_path)

    # create blank file id doesn't exist
    with open(file_save_path, "wb") as fp:
        pass

    file1 = open(file_save_path, "wb")
    file1.write(fileBytes)
    file1.close()

    # is files wasn't saved something went wrong
    if not os.path.exists(file_save_path):
        raise Exception("File was not saved correctly")
    return file_save_path


def csv_to_json(limitRows: int, file_location, headings: bool = True) -> list:
    data: list = []

    rowLimit = 0
    if headings:
        rowLimit = limitRows + 1
    else:
        rowLimit = limitRows

    json_location = file_location.split(".")[0] + ".json"

    # create blank file if doesn't exist
    with open(json_location, "wb") as fp:
        pass

    with open(file_location, encoding='utf-8') as csvf:
        csvReader = csv.reader(csvf)
        counter = 0
        for row in csvReader:
            if counter == rowLimit:  # first one is the heading
                break
            print("raw row")
            print(row)
            nested = []
            for word in row:
                nested.append(word)
            data.append(nested)
            counter += 1
    return data
