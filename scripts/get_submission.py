import gspread
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

async def get_new_submissions(last_recorded_index: int) -> List[dict]:
    """
    This function returns all the new responses from the async sign up sheet.
    """
    gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_PATH)

    sh = gc.open("Fresh Faces 3 Async Form (Responses)")

    # reads the number of responses in a required column
    records = sh.sheet1.get_all_records()
    submissions = []

    # ensure 
    for i in range(last_recorded_index + 1, len(records)):

        print(records[i])
        try:
            print(records[i][ASYNC_TIME_QUESTION])
            UTC_timestamp = records[i][ASYNC_TIME_QUESTION][3:-3]
            validate_time_check(UTC_timestamp)
            async_time_in_UTC = records[i][ASYNC_TIME_QUESTION]  # Convert to a timezone-aware datetime object in UTC
        except:
            async_time_in_UTC = "ERRORED_TIME"

        discord_id = records[i][DISCORD_ID_QUESTION] if type(records[i][DISCORD_ID_QUESTION]) == int else -1
        has_own_stream = True if records[i][UNLISTED_STREAM_LINK_QUESTION] == "Yes" else False

        submission = Response(**{
            "async_time_in_UTC": async_time_in_UTC,
            "discord_id": discord_id,
            "has_own_stream": has_own_stream,
        })

        submissions.append(submission)
    
    return submissions