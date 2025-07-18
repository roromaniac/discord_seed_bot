import pandas as pd
import datetime
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
    TOO_MANY_ASYNCS, STREAM_KEY_NOT_AVAILABLE, INVALID_TIME, INVALID_DISCORD_ID, OVERLAPPING_ASYNC, INVALID_TIMESTAMP_NOTATION, NO_UNLISTED_STREAM_PROVIDED
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
    print(username)
    return username is not None

def validate_nonoverlapping_existing_async(discord_id: int, new_async_timestamp: int, overlap_in_seconds = 3 * 60 * 60) -> bool:

    sql = """SELECT async_time_timestamp FROM async_submissions.async_submissions WHERE discord_id = %s"""
    asyncs_registered = query_database(sql, (discord_id,))
    return all([abs(new_async_timestamp - int(x[0][3:-3])) > overlap_in_seconds for x in asyncs_registered])
    
def ensure_streamkey_is_available() -> str:

    return get_available_streamkey()

def validate_timestamp_notation(async_timestamp: str) -> bool:

    try:
        int_timestamp = int(async_timestamp[3:-3])
    except ValueError:
        return False

    try:
        datetime.datetime.fromtimestamp(int_timestamp, tz=datetime.timezone.utc)
    except OSError:
        return False
    
    return True

def validate_stream_link_provided(has_own_stream: bool, unlist_stream_link: str) -> bool:

    return (not has_own_stream) or (has_own_stream and unlist_stream_link != "")

async def validate_submission(
    async_request: Response   
) -> Optional[str]:

    # ensure user actually used sesh.fyi
    if not validate_timestamp_notation(async_request.async_time_in_UTC):
        return INVALID_TIMESTAMP_NOTATION
    if not validate_stream_link_provided(async_request.has_own_stream, async_request.unlisted_stream_link):
        return NO_UNLISTED_STREAM_PROVIDED
    # if not validate_time_check(async_request.async_time_in_UTC):
    #     return INVALID_TIME
    if not validate_nonoverlapping_existing_async(async_request.discord_id, int(async_request.async_time_in_UTC[3:-3])):
        return OVERLAPPING_ASYNC
    if not await validate_discord_id(async_request.discord_id):
        return INVALID_DISCORD_ID
    if not validate_async_reg_count(async_request.discord_id):
        return TOO_MANY_ASYNCS
    if ensure_streamkey_is_available() == "":
        return STREAM_KEY_NOT_AVAILABLE
