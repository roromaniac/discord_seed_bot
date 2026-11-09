import time
import os
import asyncio

from scripts.get_submission import get_new_submissions
from scripts.validate_submission import validate_submission
from scripts.data import add_submission_to_db
from scripts.utils import (
    async_qual_hasher, 
    notify_async_participants, 
    get_discord_username, 
    get_available_streamkey, 
    construct_message, 
    send_message,
    initialize_async_cache
)

from logs.constants import INVALID_DISCORD_ID

from populate_qualifiers import main as populate_qualifiers_main

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs", "last_processed_entry.txt")

async def process_async_submissions(async_cache: list[dict]):

    # record the last processed entry
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        last_recorded_index = int(f.read().strip())
    # get all NEW async form requests since last_recorded_index
    async_submissions = await get_new_submissions(last_recorded_index)
    
    for async_submission in async_submissions:
        print("Bot Ready!")
        error_code = await validate_submission(async_submission)
        print(error_code)
        seed_number = async_qual_hasher(discord_id=async_submission.discord_id)
        stream_key = get_available_streamkey() if not async_submission.has_own_stream else "YOUTUBE"
        discord_name = await get_discord_username(async_submission.discord_id)

        if error_code is None:
            async_cache.append({
                "discord_id": async_submission.discord_id,
                "discord_username": discord_name,
                "async_timestamp_str": async_submission.async_time_in_UTC,
                "stream_key": stream_key,
                "initial_notif": False,
                "yt_live_notif": False,
                "streaming_notif": False,
                "seed_notif": False,
                "seed_number": seed_number,
            })
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
            if error_code != INVALID_DISCORD_ID:
                ### SEND A MESSAGE TO USER INDICATING FAILURE.
                message = construct_message(discord_name, message_type="initial", async_timestamp=async_submission.async_time_in_UTC, error_text=error_code)
                await send_message(message, async_submission.discord_id)

    # once a minute (or something) send out the discord messages to anyone who submitted an async
    new_async_cache = await notify_async_participants(async_cache)

    # update last processed entry
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(str(last_recorded_index + len(async_submissions)))

    # return the new async cache
    return new_async_cache

async def main():
    COUNTER = 0
    print("BOT IS LIVE")
    async_cache = await initialize_async_cache()
    while True:
        COUNTER += 1
        if COUNTER == 6:
            async_cache = await process_async_submissions(async_cache)
            COUNTER = 0
        # Run populate_qualifiers_main after processing async submissions
        populate_qualifiers_main()
        await asyncio.sleep(10)  # Wait for 60 seconds before running again

if __name__ == "__main__":
    asyncio.run(main())