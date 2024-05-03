import gspread
from gspread import Spreadsheet, Worksheet


class CacheArea:
    def __init__(self, start_col: str, end_col: str, start_row: int, end_row: int) -> None:
        self.__start_col = start_col
        self.__end_col = end_col
        self.__start_row = start_row
        self.__end_row = end_row

    def get_start_col(self) -> str:
        return self.__start_col

    def get_end_col(self) -> str:
        return self.__end_col

    def get_start_row(self) -> int:
        return self.__start_row

    def get_end_row(self) -> int:
        return self.__end_row

    def get_area(self) -> dict:
        area: dict = {}
        area['start_col'] = self.__start_col
        area['end_col'] = self.__end_col
        area['start_row'] = self.__start_row
        area['end_row'] = self.__end_row
        return area


class BaseSheet:
    def __init__(self, area: CacheArea, worksheet: Worksheet) -> None:
        self.__cache_area: CacheArea = area
        self.__ws: Worksheet = worksheet
        self.__data_cache: list[list[str]] = None
        self.__cache_is_fresh = False

    def refresh_cache(self):
        if self.__ws is None:
            return
        if self.__cache_is_fresh:
            return
        sheet_area: str = f"{self.__cache_area.get_start_col()}{self.__cache_area.get_start_row()}:{self.__cache_area.get_end_col()}{self.__cache_area.get_end_row()}"
        self.__data_cache = self.__ws.get(sheet_area)
        self.__cache_is_fresh = True

    def _get_val(self, row: int, col: int):
        if self.__ws is None:
            return ''
        try:
            return self.__data_cache[row - 1][col - 1]
        except:
            return ''

    def _get_worksheet(self) -> Worksheet:
        return self.__ws

    def invalidate_cache(self) -> None:
        self.__cache_is_fresh = False
