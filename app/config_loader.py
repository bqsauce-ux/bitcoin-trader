import json
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


CONFIG_FILE = "../config/config.json"

#BASE_DIR = Path(__file__).resolve().parent.parent
#CONFIG_FILE = BASE_DIR / "config" / "config.json"

CREDENTIALS_FILE = (
    "../credentials/google-service-account.json"
)


def load_local_config():
    """Load the local configuration file."""

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def connect_to_google_sheets():
    """Create an authenticated Google Sheets API client."""

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    service = build(
        "sheets",
        "v4",
        credentials=credentials
    )

    return service


def get_google_sheet_config():
    """Read configuration values from Google Sheets."""

    config = load_local_config()

    spreadsheet_id = config["config_source"]["spreadsheet_id"]
    worksheet_name = config["config_source"]["worksheet_name"]

    service = connect_to_google_sheets()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=worksheet_name
        )
        .execute()
    )

    values = result.get("values", [])

    return values
def convert_config_values(rows):
    """
    Convert Google Sheet rows into a Python dictionary.

    Expected format:

        parameter | value
        budget_usd | 10000
        dca_drop_pct | 3
    """

    config = {}

    for row in rows:

        if len(row) < 2:
            continue

        parameter = row[0].strip()
        value = row[1].strip()

        if not parameter:
            continue

        # Boolean values
        if value.upper() == "TRUE":
            value = True

        elif value.upper() == "FALSE":
            value = False

        # Numeric values
        else:

            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)

            except ValueError:
                # Keep strings as strings
                pass

        config[parameter] = value

    return config
