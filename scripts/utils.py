import discord
import os
import random
import pandas as pd
from copy import deepcopy

from dotenv import load_dotenv
from discord.ext import commands
import datetime

from typing import Optional

load_dotenv()

def send_message(message: str, recipient_id: int):

    bot = commands.Bot(command_prefix="!")
    
    discord_client = discord.Client()
    discord_client.run(os.getenv("DISCORD_TOKEN"))

def get_streaming_text(stream_url: str, stream_key: Optional[str]):
    if stream_url:
        return (
            f"You have indicated you wish to stream to an UNLISTED channel on the channel with the URL {stream_url}."
        )
    else:
        return (
            f"The stream key you will be streaming to is ||{stream_key}||."
        )

def construct_message(discord_user: str, async_timestamp: str, message_type: str, stream_key: str, is_own_stream: bool, error_text: Optional[str]=None) -> str:
    """
    Build a message for the user, changing the text based on whether they have a stream key.
    """
    # Example: If the user has their own stream key, give one message, otherwise another.
    if message_type == "initial":
        if error_text:
            message = (
                f"Hello {discord_user},\n\n"
                f"Thanks again for joining us for Fresh Faces 3! Your async qualifier is scheduled for {async_timestamp}.\n"
                f"Unfortunately, something went wrong. We received the error code:\n\n"
                f"{error_text}\n\n"
                f"Please follow the instructions included **which may involve you resubmitting the async request form.**"
            )
        else:
            message = (
                f"Hello {discord_user},\n\n"
                f"Your async match is scheduled for {async_timestamp}.\n"
                f"Congratulations! Your request has gone through successfully! Please note we will send you instructions for streaming 30 minutes prior to your async and the seed 15 minutes before."
            )
    
    elif message_type == "streaming":
        message = (
            f"Hello! If you're receiving this message, it is because in 30 minutes, your async qualifier will begin!\n"
            f""{get_streaming_text(stream_url=stream_key if is_own_stream else "", stream_key=stream_key)}
        )
    elif message_type == "seed":
        message = (
            
        )
    return message

def get_available_streamkey(async_schedule: pd.DataFrame) -> str:
    
    available_keys = os.getenv("STREAM_KEYS").split(",")

    for async_time in async_schedule:
        # check that the async period does not overlap with any other existing async period (4 hour period)

        # if it does...
        available_keys.drop(async_time['stream_key'])
    
    if len(available_keys) == 0:
        return ""
    else:
        return random.choice(available_keys)
    
def async_qual_hasher(timestamp: str) -> int:

    return hash(timestamp) % 4

def notify_async_participants(
        minutes_before_24_hour_YTLive_VERIFICATION: int = 48 * 60,
        minutes_before_stream_instructions: int = 30, 
        minutes_before_seed_distribution: int = 15,
    ):
    """
        A function that sends all of the necessary async information to discord users who request an async.
    """
    
    async_submissions = pass # read in the official table
    current_time = datetime.now(datetime.UTC)
    time_until_async = (async_submission['async_timestamp'] - current_time)

    for async_submission in async_submissions:

        if not async_submission['inital_notif']:
            message_type = "initial"
        if not async_submission['yt_live_notif'] and time_until_async <= minutes_before_24_hour_YTLive_VERIFICATION:
            message_type = "yt_live"    
        elif not async_submission['streaming_notif'] and time_until_async <= minutes_before_stream_instructions:
            message_type = "streaming"
        elif not async_submission['seed_notif'] and time_until_async <= minutes_before_seed_distribution:
            message_type = "seed"  
  
        message = construct_message(async_submission['discord_user'], async_submission['discord_timestamp'], message_type=message_type, error_text=async_submission['invalid_reason'])
        send_message(message, async_submission['discord_id'])