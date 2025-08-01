# 📁 storage/upload_to_gdrive.py
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def upload_to_gdrive(local_path: str, gdrive_folder_id: str = None) -> str:
    """
    Upload the file at local_path to Google Drive.
    If gdrive_folder_id is provided, upload it to that folder.
    Returns the file ID of the uploaded file.
    """
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_name = os.path.basename(local_path)
    gfile = drive.CreateFile({'title': file_name})
    if gdrive_folder_id:
        gfile['parents'] = [{'id': gdrive_folder_id}]
    gfile.SetContentFile(local_path)
    gfile.Upload()
    print(f"☁️ Uploaded to Google Drive: {file_name} (ID: {gfile['id']})")
    return gfile['id']

