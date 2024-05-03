import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Функція для отримання тренувань певної людини з Google Таблиці
def get_person_trainings(person_name):
    # Налаштовуємо доступ до Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    # Відкриваємо таблицю за посиланням
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1e2AICHQz2LFUHFmZqWTvls3NeLR5xBvsGmEtmCarCog/edit#gid=1423427296')
    
    # Вибираємо другий лист (sheet2) з таблиці
    worksheet = sheet.get_worksheet(1)
    
    # Отримуємо всі дані з другого листа
    all_data_with_indices = worksheet.get_all_values()  # Пропускаємо рядок заголовків
    all_data = worksheet.get_all_values()
    indices = [i + 1 for i in range(len(all_data))]
    date_column = 1
    time_column = 2
    # Шукаємо тренування, на які записана певна людина
    person_trainings = []
    row_indices = []
    for index, row in zip(indices, all_data_with_indices):  # Пропускаємо рядок заголовків
        if row and row[1] == person_name:
            if 4<=index <= 25:
                person_trainings.append(f'{worksheet.cell(2, 1).value} {worksheet.cell(2, 2).value}')  # Додаємо дату тренування
            elif 31<=index < 52:
                person_trainings.append(f'{worksheet.cell(29, 1).value} {worksheet.cell(29, 2).value}')
            elif 58<=index < 79:
                person_trainings.append(f'{worksheet.cell(56, 1).value} {worksheet.cell(56, 2).value}')
            elif 85<=index < 106:
                person_trainings.append(f'{worksheet.cell(83, 1).value} {worksheet.cell(83, 2).value}')
            elif 112<=index < 133:
                person_trainings.append(f'{worksheet.cell(110, 1).value} {worksheet.cell(110, 2).value}')
    
    return person_trainings



person_name = 'Волкова Света'  # Замініть на ім'я потрібної людини
trainings = get_person_trainings(person_name)
print("Тренування, на які записана {}: {}".format(person_name, trainings))
