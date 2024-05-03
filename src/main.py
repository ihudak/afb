from Bot import Bot
from SpreadSheetManager import SpreadSheetManager
import os

# default_spreadsheet_url = "https://docs.google.com/spreadsheets/d/14E8EAsCUG3elsUzpTexWdT320VmYvuypZtsa-TtzyxE/edit#gid=0"
admin_id: int = 413423581
default_spreadsheet_url: str = "https://docs.google.com/spreadsheets/d/1pe9KsEO1oqhAb0pHY7h-Q9mb_uuz4GtOH-QRNasb1y4/edit#gid=1993409970"
spreadsheet_auth_file: str = './spreadsheet_auth.json'

token_file = './telegram.token'
token: str = os.getenv("FITNESS_BOT_TOKEN")
if token is None:
    with open(token_file, 'r') as file:
        token = file.read()

env_admin = os.getenv("FITNESS_BOT_ADMIN")
if env_admin is not None and env_admin.isdigit():
    admin_id = int(env_admin)

spreadsheet_url: str = os.getenv("FITNESS_BOT_SPREADSHEET_URL")
if spreadsheet_url is None or spreadsheet_url == '':
    spreadsheet_url = default_spreadsheet_url

ssm: SpreadSheetManager = SpreadSheetManager(spreadsheet_url, spreadsheet_auth_file)
bot: Bot = Bot(token=token, fitness_sheet=ssm.get_fitness(), admin_id=admin_id)
