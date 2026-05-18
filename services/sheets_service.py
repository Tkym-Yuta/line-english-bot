import os
from pathlib import Path

import google.auth
import gspread
from google.oauth2.service_account import Credentials

from services.settings import get_required_env


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if credentials_path:
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES,
        )
    elif Path("credentials.json").exists():
        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=SCOPES,
        )
    else:
        creds, _ = google.auth.default(scopes=SCOPES)

    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    return client.open_by_key(get_required_env("SPREADSHEET_ID"))


def get_worksheet(sheet_name: str):
    spreadsheet = get_spreadsheet()

    return spreadsheet.worksheet(sheet_name)

def append_row(sheet_name: str, row: list) -> None:
    worksheet = get_worksheet(sheet_name)
    worksheet.append_row(row)
