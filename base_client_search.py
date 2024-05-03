import gspread
from oauth2client.service_account import ServiceAccountCredentials

def client(name_surname):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('ваші креденщели.json', scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_url('ваше посилання на табилцю')

    sheet = spreadsheet.sheet1
    cell = sheet.find(F"{name_surname}", in_column=3)
    if cell is not None:
        print('Ви вже є нашим клієнтом')
    else:
        name_col=sheet.col_values(3)
        cell = sheet.find(name_col[-1], in_column=3)
        row = cell.row + 1  
        colum = cell.col  
        sheet.update_cell(row, 3, name_surname)
        return row


name_surname = "Mr vaaqfwvavfqwvava "

client(name_surname)
