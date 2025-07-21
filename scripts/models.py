from pydantic import BaseModel

class Response(BaseModel):
    async_time_in_UTC: str
    discord_id: int
    has_own_stream: bool