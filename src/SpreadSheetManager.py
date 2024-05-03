import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
from FitnessSheet import FitnessSheet
from ConfigSheet import ConfigSheet
from ClientSheet import ClientSheet


class SpreadSheetManager:
    __sheet_names: dict = {
        'clients': 'Клієнти',
        'config': 'Config'
    }

    def __init__(self, url: str, auth_file: str) -> None:
        self.__gc: Client = gspread.service_account(auth_file)
        self.__sh: Spreadsheet = self.__gc.open_by_url(url)
        worksheets: list[Worksheet] = self.__sh.worksheets()
        self.__config_sheet: ConfigSheet = None
        self.__clients_sheet: ClientSheet = None
        for ws in worksheets:
            if ws.title == SpreadSheetManager.__sheet_names['config']:
                self.__config_sheet: ConfigSheet = ConfigSheet(ws)
            elif ws.title == SpreadSheetManager.__sheet_names['clients']:
                self.__clients_sheet: ClientSheet = ClientSheet(ws)
        self.__fitenss_sheet: FitnessSheet = FitnessSheet(self.__sh, self.__clients_sheet, self.__config_sheet)

    def get_fitness(self) -> FitnessSheet:
        return self.__fitenss_sheet

    def get_config(self) -> ConfigSheet:
        return self.__config_sheet

    def get_clients(self) -> ClientSheet:
        return self.__clients_sheet
