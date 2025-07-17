import gspread
import os
from datetime import datetime, timezone

from logs.constants import (
    ASYNC_TIME_QUESTION,
    DISCORD_ID_QUESTION,
    UNLISTED_STREAM_LINK,
    UNLISTED_STREAM_LINK_QUESTION
)

from pydantic import BaseModel
from typing import List, Optional

class Response(BaseModel):
    async_time_in_UTC: str
    discord_id: int
    has_own_stream: bool
    unlisted_stream_link: str

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_SHEETS_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "service_account.json")

def get_new_submissions(last_recorded_index: int) -> List[dict]:
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

        submission = Response(**{
            "async_time_in_UTC": records[i][ASYNC_TIME_QUESTION], # Convert to a timezone-aware datetime object in UTC
            "discord_id": records[i][DISCORD_ID_QUESTION],
            "has_own_stream": True if records[i][UNLISTED_STREAM_LINK_QUESTION] == "Yes" else False,
            "unlisted_stream_link": records[i][UNLISTED_STREAM_LINK]
        })
        submissions.append(submission)
    
    return submissions