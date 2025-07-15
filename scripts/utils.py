import discord
import os
import random
import pandas as pd
from copy import deepcopy

from dotenv import load_dotenv
from discord.ext import commands

from typing import Optional

load_dotenv()

def send_message(message: str, recipient_id: int):

    bot = commands.Bot(command_prefix="!")
    
    discord_client = discord.Client()
    discord_client.run(os.getenv("DISCORD_TOKEN"))

def construct_message(discord_user: str, async_timestamp: str, message_type: str, error_text: Optional[str]=None) -> str:
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
                f"Please follow the instructions included **which may involve you resubmitting the async request form**"
            )
        else:
            message = (
                f"Hello {discord_user},\n\n"
                f"Your async match is scheduled for {async_timestamp}.\n"
                f"Congratulations! Your request has gone through successfully! Please note we will send you instructions for streaming 30 minutes prior to your async and the seed 15 minutes before."
            )
    
    elif message_type == "streaming":
        message = "COMING SOON"
    elif message_type == "seed":
        message = "COMING SOON"
    return message

def get_available_streamkey(async_schedule: pd.DataFrame) -> str:
    
    available_keys = os.getenv("STREAM_KEYS").split(",")

    for async_time in async_schedule:
        # check that the async period does not overlap with any other existing async period (4 hour period)

        # if it does...
        available_keys.drop(async_time['stream_key'])
    
    if len(available_keys) == 0:
        return -1
    else:
        return random.choice(available_keys)
    
def async_qual_hasher(timestamp: str) -> int:

    return hash(timestamp) % 4

def notify_async_participants(
        minutes_before_stream_instructions: int = 30, 
        minutes_before_seed_distribution=15
    ):
    """
        A function that sends all of the necessary async information to discord users who request an async.
    """
    pass