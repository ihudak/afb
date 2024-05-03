from gspread import Spreadsheet, Worksheet, Cell
from BaseSheet import CacheArea, BaseSheet
from Client import Client


class ClientSheet(BaseSheet):
    __max_row_config = 500
    __first_col_config = 'A'
    __last_col_config = 'B'

    def __init__(self, client_worksheet: Worksheet) -> None:
        area: CacheArea = CacheArea(start_col=ClientSheet.__first_col_config, end_col=ClientSheet.__last_col_config, start_row=1, end_row=ClientSheet.__max_row_config)
        super().__init__(area=area, worksheet=client_worksheet)
        self.__conf = {}
        self.refresh_cache()

    def add_client(self, client: Client) -> None:
        row_num: int = self.__find_row_num(client)
        if row_num > 0:
            self.__write_client(client, row_num)
            client.set_created()

    def __find_row_num(self, client: Client) -> int:
        col_num: int = 2
        for r in range(2, ClientSheet.__max_row_config):
            current_value: str = self._get_val(r, col_num)
            if current_value == client.get_phone():
                return 0  # client is found. No need to add
            elif current_value == "":  # end of data on the  sheet. Client is not there
                return r
        return 0  # end of sheet. Client is not there

    def __write_client(self, client: Client, row_num: int) -> None:
        col_num: int = 1
        cells: list[Cell] = []
        cells.append(Cell(row_num, col_num, client.get_id()))
        col_num += 1
        cells.append(Cell(row_num, col_num, client.get_phone()))
        col_num += 1
        cells.append(Cell(row_num, col_num, client.get_name()))
        self._get_worksheet().update_cells(cells)
        self.invalidate_cache()
