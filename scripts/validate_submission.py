import pandas as pd
import discord
import os
import asyncio
from scripts.get_submission import Response

from typing import Optional

from scripts.utils import (
    get_available_streamkey,
)

from scripts.data import (
    load_config, connect, query_database
)

from logs.constants import (
    TOO_MANY_ASYNCS, STREAM_KEY_NOT_AVAILABLE, INVALID_TIME, INVALID_DISCORD_ID
)

from scripts.utils import get_discord_username

def validate_time_check(UTC_time: int) -> bool:

    # extract timestamp int
    UTC_time = int(UTC_time[3:-3])

    # ensure it is between the July 24, 12pm EDT and July 31, 10pm EDT
    asyncs_open = 1753372800
    asyncs_close = 1754013600

    return asyncs_open <= UTC_time <= asyncs_close

def validate_async_reg_count(discord_id: int, allowed_asyncs: int = 2) -> bool:

    # ensure the entrant has not registered twice before
    # some sql code that checks how many times they have signed up before (ACCOUNT FOR INVALID SUBMISSIONS)
    sql = """SELECT seed_number FROM async_submissions.async_submissions WHERE discord_id = %s"""
    asyncs_played = query_database(sql, (discord_id,))
    return len(asyncs_played) < allowed_asyncs

async def validate_discord_id(discord_id: int) -> bool:
    
    username = await get_discord_username(discord_id)
    print(username, username is not None)
    return username is not None

def validate_nonoverlapping_existing_async(discord_id: int) -> bool:

    pass
    
def ensure_streamkey_is_available() -> str:

    return get_available_streamkey()

async def validate_submission(
    async_request: Response   
) -> Optional[str]:

    # if not validate_time_check(async_request.async_time_in_UTC):
    #     return INVALID_TIME
    if not await validate_discord_id(async_request.discord_id):
        return INVALID_DISCORD_ID
    if not validate_async_reg_count(async_request.discord_id):
        return TOO_MANY_ASYNCS
    if ensure_streamkey_is_available() == "":
        return STREAM_KEY_NOT_AVAILABLE
