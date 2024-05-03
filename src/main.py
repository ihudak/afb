from Bot import Bot
from SpreadSheetManager import SpreadSheetManager
import os

# SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14E8EAsCUG3elsUzpTexWdT320VmYvuypZtsa-TtzyxE/edit#gid=0"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1pe9KsEO1oqhAb0pHY7h-Q9mb_uuz4GtOH-QRNasb1y4/edit#gid=1993409970"
spreadsheet_auth_file = './spreadsheet_auth.json'
token_file = './telegram.token'
TOKEN = os.getenv("FITNESS_BOT_TOKEN")
if TOKEN is None:
    with open(token_file, 'r') as file:
        TOKEN = file.read()

ssm: SpreadSheetManager = SpreadSheetManager(SPREADSHEET_URL, spreadsheet_auth_file)
bot: Bot = Bot(TOKEN, ssm.get_fitness())
