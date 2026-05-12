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