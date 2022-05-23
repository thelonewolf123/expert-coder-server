from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from dotenv import dotenv_values

import dropbox
import os


def get_dropbox_object():
    config = dotenv_values()


    dropbox_token = config.get('DROPBOX_TOKEN')
    if dropbox_token == None:
        dropbox_token = os.environ.get('DROPBOX_TOKEN')


    dbx = dropbox.Dropbox(dropbox_token)
    return dbx



def upload_file_to_dropbox(file_obj, filepath):
    try:
        dbx = get_dropbox_object()
        dbx.files_upload(file_obj.read(), filepath,
                         mode=WriteMode('overwrite'))
    except ApiError as err:
        # This checks for the specific error where a user doesn't have
        # enough Dropbox space quota to upload this file
        if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
            print("ERROR: Cannot upload file; insufficient space.")
        elif err.user_message_text:
            print(err.user_message_text)
        else:
            print(err)


def get_file_from_dropbox(path):
    # generate a stream link for file download
    dbx = get_dropbox_object()
    url = dbx.files_get_temporary_link(path).link
    return url
