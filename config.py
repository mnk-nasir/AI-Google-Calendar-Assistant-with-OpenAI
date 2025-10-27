import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    OPENAI_API_KEY: str
    GOOGLE_API_TOKEN: str
    CALENDAR_ID: str
    TIMEZONE: str
    mock: bool

    @staticmethod
    def load_from_env() -> "Config":
        oa = os.getenv("OPENAI_API_KEY", "")
        g = os.getenv("GOOGLE_API_TOKEN", "")
        c = os.getenv("CALENDAR_ID", "")
        tz = os.getenv("TIMEZONE", "Europe/Paris")
        mock = not (oa and g and c)
        return Config(oa, g, c, tz, mock)
