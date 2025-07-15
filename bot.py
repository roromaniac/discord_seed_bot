import discord
import gspread
import time
import os

from pydantic import BaseModel
from typing import List, Optional

from scripts.get_submission import get_submissions
from scripts.validate_submission import validate_submission
from scripts.data import add_submission_to_db
from scripts.utils import async_qual_hasher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs", "last_processed_entry.txt")

if __name__ == "__main__":

    # once a minute
    # time.sleep(60)

    # record the last processed entry
    with open(LOG_PATH, "r") as f:
        last_recorded_index = int(f.read().strip())
    # get all NEW async form requests since last_recorded_index
    async_submissions = get_new_submissions(last_recorded_index)
    
    for async_submission in async_submissions:
        error_code = validate_submission(async_submission)
        seed_number = async_qual_hasher(async_submission.timestamp_of_original_request)
        add_submission_to_db(async_submission, error_code, seed_number)
    # update last processed entry
    with open(LOG_PATH, "w") as f:
        f.write(last_recorded_index + len(async_submissions))

    # once a minute (or something) send out the discord messages to anyone who submitted an async
    notify_async_participants(async_db)



