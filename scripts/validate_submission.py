import pandas as pd
import discord
from scripts.get_submission import Response

from typing import Optional

from scripts.utils import (
    get_available_streamkey,
)

from scripts.data import (
    load_config, connect
)

from logs.constants import (
    TOO_MANY_ASYNCS, STREAM_KEY_NOT_AVAILABLE, INVALID_TIME, INVALID_DISCORD_ID
)

def validate_time_check(UTC_time: int) -> bool:

    # ensure it is between the July 24, 12pm EDT and July 31, 10pm EDT
    asyncs_open = 1753372800
    asyncs_close = 1754013600

    return asyncs_open <= UTC_time <= asyncs_close



def validate_async_reg_count(current_asyncs_db: pd.DataFrame, allowed_asyncs: int = 2) -> bool:

    # ensure the entrant has not registered twice before
    # some sql code that checks how many times they have signed up before (ACCOUNT FOR INVALID SUBMISSIONS)
    pass

async def validate_discord_id(discord_id: int) -> bool:

    intents = discord.Intents.default()
    intents.members = True  # Need this to see members

    client = discord.Client(intents=intents)

    # ensure the discord id fetched a valid user
    try:
        user = await client.fetch_user(discord_id)
        print("Recording user: {user}")
    except discord.NotFound as e:
        user = "There is no user with this discord id."
    
    return user != "There is no user with this discord id."
    
    
def ensure_streamkey_is_available() -> str:

    return get_available_streamkey()

def validate_submission(
    async_request: Response   
) -> Optional[str]:

    if not validate_time_check(async_request.async_time_in_UTC):
        return INVALID_TIME
    if not validate_discord_id(async_request.discord_id):   
        # send error message to user
        return INVALID_DISCORD_ID
    if not validate_async_reg_count(async_request.discord_id):
        # send error message to user
        return TOO_MANY_ASYNCS
    if ensure_streamkey_is_available() == -1:
        # send error message to user
        return STREAM_KEY_NOT_AVAILABLE


    

