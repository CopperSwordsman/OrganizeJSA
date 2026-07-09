import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GUILD_ID = int(os.getenv("GUILD_NUM"))

#the offcer role ID is chair board in this case
OFFICER_ROLE_ID = 1467212936677167106
MULTIMEDIA_ROLE_ID = 1504916667283669183