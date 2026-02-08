import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DB = os.getenv("SQL_DB")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_DRIVER = os.getenv("SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")

    COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY = os.getenv("COSMOS_KEY")

    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
    SEARCH_KEY = os.getenv("SEARCH_KEY")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()
