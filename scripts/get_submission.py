import gspread_asyncio
import os
from datetime import datetime, timezone

from logs.constants import (
    ASYNC_TIME_QUESTION,
    DISCORD_ID_QUESTION,
    UNLISTED_STREAM_LINK_QUESTION,
    INVALID_TIMESTAMP_NOTATION
)

from scripts.models import Response
from typing import List, Optional

from scripts.validate_submission import validate_time_check
from scripts.utils import send_message, construct_message, get_discord_username

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_SHEETS_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "service_account.json")

def get_creds():
    import os
    from google.oauth2.service_account import Credentials
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GOOGLE_SHEETS_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "service_account.json")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    return Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_PATH, scopes=scopes)

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

async def get_new_submissions(last_recorded_index: int) -> List[dict]:
    """
    This function returns all the new responses from the async sign up sheet.
    """
    agc = await agcm.authorize()
    sh = await agc.open("Fresh Faces 3 Async Form (Responses)")
    worksheet = await sh.get_worksheet(0)  # 0 = first sheet

    records = await worksheet.get_all_records()
    submissions = []

    for i in range(last_recorded_index + 1, len(records)):
        print(records[i])
        try:
            print(records[i][ASYNC_TIME_QUESTION])
            UTC_timestamp = records[i][ASYNC_TIME_QUESTION][3:-3]
            validate_time_check(UTC_timestamp)
            async_time_in_UTC = records[i][ASYNC_TIME_QUESTION]
        except:
            async_time_in_UTC = "ERRORED_TIME"

        try: 
        	discord_id = int(records[i][DISCORD_ID_QUESTION])
        except ValueError:
            discord_id = -1
        has_own_stream = True if records[i][UNLISTED_STREAM_LINK_QUESTION] == "Yes" else False

        submission = Response(**{
            "async_time_in_UTC": async_time_in_UTC,
            "discord_id": discord_id,
            "has_own_stream": has_own_stream,
        })

        submissions.append(submission)
    
    return submissions