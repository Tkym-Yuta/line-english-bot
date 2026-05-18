import gspread
from google.oauth2.service_account import Credentials

def get_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=scope
    )
    return gspread.authorize(creds)

def get_words():
    client = get_client()
    sheet = client.open_by_key("YOUR_SPREADSHEET_ID")
    ws = sheet.worksheet("Words")
    return ws.get_all_records()

# -------------------------------
import gspread

from config import SPREADSHEET_ID

client = gspread.service_account(filename="credentials.json")

spreadsheet = client.open_by_key(SPREADSHEET_ID)

def get_worksheet(sheet_name: str):

    return spreadsheet.worksheet(sheet_name)

def append_row(sheet_name: str, row: list) -> None:
    worksheet = get_worksheet(sheet_name)
    worksheet.append_row(row)