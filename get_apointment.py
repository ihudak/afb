import gspread
from oauth2client.service_account import ServiceAccountCredentials




scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
    
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1e2AICHQz2LFUHFmZqWTvls3NeLR5xBvsGmEtmCarCog/edit#gid=1423427296')

def get_apointment_for_tables_1_and_3(person_name):
    #Працює для 2 та 4 листка 
    worksheet = sheet.get_worksheet(1) 
    
    # Отримуємо всі дані з другого листа 
    all_data_with_indices = worksheet.get_all_values()
    all_data = worksheet.get_all_values()
    indices = [i + 1 for i in range(len(all_data))]
    date_column = 1
    time_column = 2
    # Шукаємо тренування, на які записана певна людина
    person_trainings = []
    row_indices = []
    for index, row in zip(indices, all_data_with_indices):  # Пропускаємо рядок заголовків
        if row and row[1] == person_name:
            # Визначаємо рядок для дати та тренування
            date_row = ((index - 4) // 24) * 24 + 2
            time_row = date_row

            # Додаємо дату та тренування до списку
            person_trainings.append(f'{worksheet.cell(date_row, date_column).value} {worksheet.cell(time_row, time_column).value}')
    
    return person_trainings



person_name = 'Волкова Света'
trainings = get_apointment_for_tables_1_and_3(person_name)
print("Тренування, на які записана {}: {}".format(person_name, trainings))

def get_apointment_for_tables_2_and_4(person_name):
    #Працює для 3 та 5 листка 
    worksheet = sheet.get_worksheet(2) 
    
    # Отримуємо всі дані з другого листа 
    all_data_with_indices = worksheet.get_all_values()
    all_data = worksheet.get_all_values()
    indices = [i + 1 for i in range(len(all_data))]
    date_column = 1
    time_column = 2
    # Шукаємо тренування, на які записана певна людина
    person_trainings = []
    row_indices = []
    for index, row in zip(indices, all_data_with_indices):  # Пропускаємо рядок заголовків
        if row and row[1] == person_name:
            # Визначаємо рядок для дати та тренування
            date_row = ((index - 4) // 27) * 27 + 2
            time_row = date_row

            # Додаємо дату та тренування до списку
            person_trainings.append(f'{worksheet.cell(date_row, date_column).value} {worksheet.cell(time_row, time_column).value}')
    
    return person_trainings


person_name = 'Кравчук Марія'
trainings = get_apointment_for_tables_2_and_4(person_name)
print("Тренування, на які записана {}: {}".format(person_name, trainings))