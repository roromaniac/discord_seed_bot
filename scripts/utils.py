import discord
import os
import random
import psycopg2
import datetime
import pandas as pd
from copy import deepcopy

from dotenv import load_dotenv
from discord.ext import commands
import datetime

from typing import Optional

from scripts.data import load_config, query_database
from scripts.discord_client import FetchUserClient, SendUserMessage, SendUserImage, get_discord_username

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(BASE_DIR, "seeds")

async def send_message(message: str, recipient_id: int):

    intents = discord.Intents.default()
    client = SendUserMessage(recipient_id, message, intents=intents)
    await client.start(os.getenv("DISCORD_TOKEN"))
    await client.http.close()  # Explicitly close the HTTP session

async def send_seed_png(file: discord.File, recipient_id: int):
    intents = discord.Intents.default()
    client = SendUserImage(recipient_id, file, intents=intents)
    await client.start(os.getenv("DISCORD_TOKEN"))
    await client.http.close()  # Explicitly close the HTTP session

def get_streaming_text(is_our_key: bool, stream_key: Optional[str]):
    if is_our_key:
        return (
            f"The stream key you will be streaming to is \n\n||{stream_key}||\n\n"
        )
    else:
        return (
            "You have indicated you wish to stream to an UNLISTED channel.\n\n"
        )

def construct_message(
        discord_user: str, 
        message_type: str, 
        async_timestamp: Optional[str]=None, 
        stream_key: Optional[str]=None, 
        error_text: Optional[str]=None,
        seed_number: Optional[int]=None,
    ) -> str:
    """
    Build a message for the user, changing the text based on whether they have a stream key.
    """

    if message_type == "initial":
        if error_text:
            message = (
                f"Hello {discord_user},\n\n"
                f"Thanks again for joining us for Fresh Faces 3! You attempted to schedule your async qualifier for {async_timestamp}.\n"
                f"Unfortunately, something went wrong. We received the error code:\n\n"
                f"{error_text}\n\n"
                f"Please follow the instructions included **which may involve you resubmitting the async request form.**"
            )
        else:
            message = (
                f"Hello {discord_user},\n\n"
                f"Your async is scheduled for {async_timestamp}.\n\n"
                f"Congratulations! Your request has gone through successfully! Please note we will send you instructions for streaming 30 minutes prior to your async and the seed 15 minutes prior to your async."
            )

    elif message_type == "yt_live":

        message = (
            "Hello! If you're receiving this message, it is because within 48 hours or less of this message, you will begin your async qualifier. "
            f"We have it on record that you will be providing your OWN restream to us on an unlisted stream. "
            "We bring this up because we have observed in times past that if you have never streamed before, you need to request a stream key before you can stream which can take up to 24 hours. "
            "Please take the time to handle this now. If you need any assistance, please reach out to @Wallpesh or @Kallat."
        )
    
    elif message_type == "streaming":
        message = (
            f"Hello! If you're receiving this message, it is because in 30 minutes, your async qualifier will begin! "
            f"{get_streaming_text(is_our_key=is_our_async_account(stream_key), stream_key=stream_key)}\n"
            f"Please ensure you go live to this channel with the following assets clearly visible and non-overlapping on your overlay: \n"
            f"- Tracker\n"
            f"- Loadless Timer (RTA Timer Helpful too)\n"
            f"- KH2 Gameplay (won't be visible until you build the seed).\n\n"
            f"We will send you the seed to plug into your generator in 15 minutes!"
        )
    elif message_type == "seed":
        message = (
            "We are about to distribute the seed you need to play. Please be sure to FIRST fill out the [clock in form](https://docs.google.com/forms/d/e/1FAIpQLSdk4oddzoIT1OmTWWxXbWIHs4j-gqkzleeYz4zo4B03nc4lHA/viewform?usp=sharing&ouid=104590086266811208664). "
            "**When you are finished**, please fill out the [clock out form](https://docs.google.com/forms/d/e/1FAIpQLSdmczhfZfWJcFZItRkrphO72ktI7bxUv_kvZ-bRH-br5RA2YA/viewform?usp=sharing&ouid=104590086266811208664). \n\n"
            "Below is your seed that you must load into the generator:\n\n"
        )
        with open(os.path.join(SEED_PATH, f"seed{seed_number}.txt"), "r") as file:
            seed_content = file.read()
        message += seed_content + "\n\n"
        message += "You can load this into your generator by copying the FULL seed string and going to Share Seed -> Load Seed from Clipboard."
        message += "\n\n"
    return message

def get_available_streamkey(hours_buffer: float=4.0) -> str:
    
    available_keys = os.getenv("STREAM_KEYS").split(",")

    # Ensure that the async period does not overlap with any other existing async period (4 hour period)
    current_utc_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()  # Get the current UTC timestamp
    start_time = current_utc_timestamp - 3600 * hours_buffer  # 4 hours before the current UTC timestamp
    end_time = current_utc_timestamp + 3600 * hours_buffer  # 4 hours after the current UTC timestamp
    sql = """SELECT stream_key FROM async_submissions.async_submissions WHERE async_time_timestamp >= %s AND async_time_timestamp <= %s"""
    params = (f"<t:{start_time}:F>", f"<t:{end_time}:F>")
    overlapping_asyncs = query_database(sql, params)
    for stream_key_in_use_at_async_time in overlapping_asyncs: # each one of these is a tuple
        print(available_keys, stream_key_in_use_at_async_time[0])
        available_keys.remove(stream_key_in_use_at_async_time[0])
    
    if len(available_keys) == 0:
        return ""
    else:
        return random.choice(available_keys)
    
def async_qual_hasher(discord_id, num_async_qualifiers=4) -> int:

    # check what async qual seeds are available for a user by connecting to db
    sql = """SELECT seed_number FROM async_submissions.async_submissions WHERE discord_id = %s"""
    params = (discord_id,)
    seeds = query_database(sql, params)
    seeds = [x[0] for x in seeds]
    available_seeds = list(set(range(1, num_async_qualifiers+1)) - set(seeds))
    
    return random.choice(available_seeds)

async def notify_async_participants(
        seconds_before_24_hour_YTLive_VERIFICATION: int = 48 * 60 * 60, # 48 hours, 60 mins/hr, 60 secs/min
        seconds_before_stream_instructions: int = 30 * 60, # 30 minutes, 60 secs/min
        seconds_before_seed_distribution: int = 15 * 60, # 15 minutes, 60 secs/min
    ):
    """
        A function that sends all of the necessary async information to discord users who request an async.
    """
    
    sql = """SELECT * FROM async_submissions.async_submissions"""
    async_submissions = query_database(sql)
    current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    for async_submission in async_submissions:

        discord_id, discord_username, async_timestamp_str, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number = async_submission

        time_until_async = (int(async_timestamp_str[3:-3]) - current_time)
        
        message_type = None
        update_sql = None
        kwargs = {}

        if not initial_notif:
            message_type = "initial"
            # Update the async_submission status in the database
            update_sql = """UPDATE async_submissions.async_submissions SET initial_notif = %s WHERE discord_id = %s AND seed_number = %s"""
        elif not yt_live_notif and time_until_async <= seconds_before_24_hour_YTLive_VERIFICATION and not is_our_async_account(stream_key):
            message_type = "yt_live"
            update_sql = """UPDATE async_submissions.async_submissions SET yt_live_notif = %s WHERE discord_id = %s AND seed_number = %s"""
            kwargs = {"stream_key": stream_key}
        elif not streaming_notif and time_until_async <= seconds_before_stream_instructions:
            message_type = "streaming"
            update_sql = """UPDATE async_submissions.async_submissions SET streaming_notif = %s WHERE discord_id = %s AND seed_number = %s"""
            kwargs = {"stream_key": stream_key}
        elif not seed_notif and time_until_async <= seconds_before_seed_distribution:
            message_type = "seed"
            update_sql = """UPDATE async_submissions.async_submissions SET seed_notif = %s WHERE discord_id = %s AND seed_number = %s"""
            kwargs = {"seed_number": seed_number}

        if message_type is not None and update_sql is not None:
    
            message = construct_message(discord_username, message_type=message_type, async_timestamp=async_timestamp_str, error_text="", **kwargs)
            await send_message(message, discord_id)
            if message_type == "seed":
                seed_png_filepath = os.path.join(SEED_PATH, f"seed{seed_number}.png")
                await send_seed_png(file=discord.File(seed_png_filepath), recipient_id=discord_id)
            update_params = (True, discord_id, seed_number)
            query_database(update_sql, update_params)

def is_our_async_account(stream_key: str):

    return stream_key in os.getenv("STREAM_KEYS").split(',')