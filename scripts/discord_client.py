import discord
import asyncio
import os

class FetchUserClient(discord.Client):
    """
        A class intended for one-off, not live connections to discord to find a user.
    """
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.found_user = None

    async def on_ready(self):
        try:
            user = await self.fetch_user(self.user_id)
            print(f"Recording user: {user}")
            self.found_user = user.name
        except discord.NotFound:
            print("There is no user with this discord id.")
        await self.close()  # This will stop client.start()

class SendUserMessage(discord.Client):
    """
        A class intended for one-off, not live connections to discord to send a message to a user.
    """
    def __init__(self, user_id, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.message = message
        self.found_user = None

    async def on_ready(self):
        try:
            user = await self.fetch_user(self.user_id)
            print(f"Recording user: {user}")
            self.found_user = user
            if self.found_user is not None:
                await self.found_user.send(self.message)
        except discord.NotFound:
            print("There is no user with this discord id.")
        await self.close()  # This will stop client.start()

class SendUserImage(discord.Client):
    """
        A class intended for one-off, not live connections to discord to send a message to a user.
    """
    def __init__(self, user_id, file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.file = file
        self.found_user = None

    async def on_ready(self):
        try:
            user = await self.fetch_user(self.user_id)
            print(f"Recording user: {user}")
            self.found_user = user
            if self.found_user is not None:
                await self.found_user.send(file=self.file)
        except discord.NotFound:
            print("There is no user with this discord id.")
        await self.close()  # This will stop client.start()

async def get_discord_username(discord_id: int) -> bool:
    intents = discord.Intents.default()
    client = FetchUserClient(discord_id, intents=intents)
    try:
        await asyncio.wait_for(client.start(os.getenv("DISCORD_TOKEN")), timeout=2.5)
    except asyncio.TimeoutError:
        print("Timeout: Could not fetch user, possible invalid Discord ID.")
        await client.close()
        return None
    await client.http.close()  # Explicitly close the HTTP session
    return client.found_user