from gspread import Spreadsheet, Worksheet
from BaseSheet import CacheArea, BaseSheet
from WeekDayTranslator import WeekDayTranslator


class ConfigSheet(BaseSheet):
    __max_row_config = 500
    __first_col_config = 'B'
    __last_col_config = 'F'

    def __init__(self, config_worksheet: Worksheet) -> None:
        area: CacheArea = CacheArea(start_col=ConfigSheet.__first_col_config, end_col=ConfigSheet.__last_col_config, start_row=1, end_row=ConfigSheet.__max_row_config)
        super().__init__(area=area, worksheet=config_worksheet)
        self.__conf = {}
        self.__read_all_configs()

    def get_configs(self) -> dict:
        return self.__conf

    def get_config(self, config_name: str) -> dict:
        if config_name not in self.__conf.keys():
            return None
        return self.__conf[config_name]

    def __read_all_configs(self) -> dict:
        self.__conf = {}  # clean the config
        self.refresh_cache()
        row_num: int = 1
        while row_num > 0:
            row_num = self.__read_config(row_num)
        if len(self.__conf.keys()) == 0:
            return None
        return self.__conf

    def __read_config(self, start_row: int) -> int:
        config_size: int = 11
        config_data: dict = {}
        config_key: str = self._get_val(start_row, 1)
        if config_key == '' or start_row + config_size > self.__max_row_config:  # no further configs
            return 0
        try:
            config_data['capacity'] = int(self._get_val(start_row + 1, 1))
            config_data['reserved_capacity'] = int(self._get_val(start_row + 2, 1))
            config_data['foot_size_required'] = 'TRUE' == self._get_val(start_row + 3, 1)
            config_data['schedule'] = {}
            for i in range(start_row + 4, start_row + 11):
                config_data['schedule'][WeekDayTranslator.translate_str(i - start_row - 4)] = []
                j: int = 1
                while True:
                    sch_time = self._get_val(i, j)
                    if sch_time == '':
                        break
                    config_data['schedule'][WeekDayTranslator.translate_str(i - start_row - 4)].append(sch_time)
                    j += 1
            self.__conf[config_key] = config_data
        except:
            return 0
        return config_size + start_row
