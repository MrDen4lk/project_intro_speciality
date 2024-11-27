import os
from dotenv import load_dotenv

load_dotenv()

def database_url_asyncpg() -> str:
    return (f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}"
            f"@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}")