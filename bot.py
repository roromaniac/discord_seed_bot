import time
import os
import asyncio

from scripts.get_submission import get_new_submissions
from scripts.validate_submission import validate_submission
from scripts.data import add_submission_to_db
from scripts.utils import async_qual_hasher, notify_async_participants, get_discord_username, get_available_streamkey, construct_message, send_message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs", "last_processed_entry.txt")

async def process_async_submissions():
    # record the last processed entry
    with open(LOG_PATH, "r") as f:
        last_recorded_index = int(f.read().strip())
    # get all NEW async form requests since last_recorded_index
    async_submissions = get_new_submissions(last_recorded_index)
    
    for async_submission in async_submissions:
        error_code = await validate_submission(async_submission)
        print(error_code)
        seed_number = async_qual_hasher(discord_id=async_submission.discord_id)
        stream_key = get_available_streamkey() if async_submission.unlisted_stream_link == "" else async_submission.unlisted_stream_link
        discord_name = await get_discord_username(async_submission.discord_id)

        if error_code is None:
            add_submission_to_db(
                discord_id=async_submission.discord_id, 
                discord_name=discord_name,
                async_time_timestamp=async_submission.async_time_in_UTC,
                stream_key=stream_key,
                initial_notif=False,
                yt_live_notif=False,
                streaming_notif=False,
                seed_notif=False,
                seed_number=seed_number
            )
        else:
            ### SEND A MESSAGE TO USER INDICATING FAILURE.
            message = construct_message(discord_name, message_type="initial", async_timestamp=async_submission.async_time_in_UTC, error_text=error_code)
            await send_message(message, async_submission.discord_id)

    # once a minute (or something) send out the discord messages to anyone who submitted an async
    await notify_async_participants()

    # update last processed entry
    with open(LOG_PATH, "w") as f:
        f.write(str(last_recorded_index + len(async_submissions)))

if __name__ == "__main__":
    asyncio.run(process_async_submissions())
