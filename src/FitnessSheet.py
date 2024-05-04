from ExerciseType import ExerciseType
from Appointment import Appointment
from Exercise import Exercise
from Client import Client
from WeekDayTranslator import WeekDayTranslator
import string
from pprint import pprint
import gspread
from gspread import Cell, Client, Spreadsheet, Worksheet
from gspread.utils import rowcol_to_a1
import requests
from datetime import datetime
from ConfigSheet import ConfigSheet
from ClientSheet import ClientSheet


class FitnessSheet:
    __days_to_refresh_schedule: list[int] = [5, 6]
    __days_of_expiration_to_trigger_schedule_refresh: int = 5
    __archive_sheet_prefix: str = 'arc '
    __template_sheet_prefix: str = 'template '
    __first_col_exercises: str = 'A'
    __last_col_exercises: str = 'C'

    __data_cache: {str, list[list[str]]} = {}  # cache of the worksheets' data
    __worksheets_cache: {str, Worksheet} = {}  # cache of the worksheets

    def __init__(self, spreadsheet: Spreadsheet, clients_sheet: ClientSheet, config_sheet: ConfigSheet):
        self.__sh: Spreadsheet = spreadsheet
        self.__cache_worksheet_names()
        self.__clients_sheet = clients_sheet
        self.__config_sheet = config_sheet
        self.__cache_is_fresh: {str, bool} = {}

    def __is_worksheet_exercise_type(self, ws_name: str) -> bool:
        return ExerciseType.is_valid_name(ws_name)

    def __is_worksheet_template(self, ws_name: str) -> bool:
        return ws_name.startswith(self.__template_sheet_prefix)

    def __is_worksheet_archive(self, ws_name: str) -> bool:
        return ws_name.startswith(self.__archive_sheet_prefix)

    def __is_valid_worksheet_for_cache(self, ws_name: str) -> bool:
        return self.__is_worksheet_exercise_type(ws_name) or self.__is_this_week_archive_sheet(ws_name)

    def __is_this_week_archive_sheet(self, ws_name: str) -> bool:
        arch_prefix: str = self.__archive_current_week_prefix()
        originame_ex_type_name: str = ws_name.removeprefix(arch_prefix)
        return self.__is_worksheet_exercise_type(originame_ex_type_name)

    def get_exercise_types(self) -> list[ExerciseType]:
        self.__refresh_schedule()
        exercise_types: list[ExerciseType] = []
        for ws in self.__worksheets_cache.keys():
            if self.__is_worksheet_exercise_type(ws):
                exercise_types.append(ExerciseType(ws, self.__config_sheet))
        return exercise_types  # list of ExersiceType objects

    def get_exercises(self, exercise_type: ExerciseType) -> list[Exercise]:
        return self.__get_exercises(exercise_type, False)

    def get_available_exercises(self, exercise_type: ExerciseType, client: Client) -> list[Exercise]:
        exercises: list[Exercise] = self.__get_exercises(exercise_type=exercise_type, is_archive=False)
        if exercises is None or len(exercises) == 0:
            return []
        result: list[Exercise] = []
        for ex in exercises:
            if not self.__is_client_already_in_exercise(client=client, exercise=ex, is_archive=False) and ex.has_free_slots():
                result.append(ex)
        return result

    def __get_exercises(self, exercise_type: ExerciseType, is_archive: bool) -> list[Exercise]:
        if not exercise_type.is_valid():
            return []
        ws_name: str = self.__archive_sheet_name(exercise_type.get_name()) if is_archive else exercise_type.get_name()
        self.__invalidate_cache(ws_name)
        self.__cache_worksheet(ws_name)
        ws = self.__get_worksheet(ws_name)
        if ws is None:
            return []  # ExerciseType is not found - returning empty list
        exersises: list[Exercise] = []
        current_row: int = 1
        max_row = exercise_type.num_rows_in_worksheet()
        if is_archive:
            max_row *= 2
        while current_row < max_row:
            ex = self.__detect_next_exercise(exercise_type, current_row, is_archive)
            if ex is None:
                break
            current_row = ex.get_last_row() + 1
            if ex.is_in_future():
                exersises.append(ex)
        return exersises

    def __detect_next_exercise(self, ex_type: ExerciseType, start_row: int, is_archive: bool) -> Exercise:
        ws_name: str = self.__archive_sheet_name(ex_type.get_name()) if is_archive else ex_type.get_name()
        max_row = ex_type.num_rows_in_worksheet()
        if is_archive:
            max_row *= 2
        for r in range(start_row, max_row):
            col1_value = self.__get_val(ws_name, r, 1)
            col2_value = self.__get_val(ws_name, r, 2)
            col3_value = self.__get_val(ws_name, r, 3)
            if col1_value != '' and col2_value != '':  # exercise found
                ex = Exercise(ex_type, col1_value, col2_value, col3_value, r)
                if not is_archive:
                    self.__detect_free_slots_exersise(ex)
                return ex
        return None  # End of the worksheet. no more exersizes

    def __detect_free_slots_exersise(self, ex: Exercise):
        usr_col = 3
        for r in range(ex.get_capacity_start_row(), ex.get_capacity_end_row() + 1):
            current_value = self.__get_val(ex.get_type().get_name(), r, usr_col)
            if current_value == '':  # found an empty slot
                ex.set_free_slots(ex.get_capacity_end_row() - r + 1 + ex.get_type().get_reserve_capacity())
                return
        for r in range(ex.get_start_reserve_row(), ex.get_end_reserve_row() + 1):
            current_value = self.__get_val(ex.get_type().get_name(), r, usr_col)
            if current_value == '':  # found an empty slot
                ex.set_free_slots(ex.get_end_reserve_row() - r + 1)
                return
        ex.set_free_slots(0)  # if we are here then no slots remain

    def make_appointment(self, appointment: Appointment) -> Appointment:
        if appointment is None or appointment.get_exercise() is None or appointment.get_client() is None:
            return None
        self.__clients_sheet.refresh_cache()
        self.__clients_sheet.add_client(appointment.get_client())
        self.__cache_worksheet(appointment.get_exercise().get_type().get_name())
        self.__add_client_in_exercise(appointment)
        return appointment

    def get_appointments(self, client: Client, include_archive: bool) -> list[Appointment]:
        appointmens: list[Appointment] = []
        exercise_types: list[ExerciseType] = self.get_exercise_types()
        for et in exercise_types:
            arch_exercises: list[Exercise] = self.__get_exercises(et, True) if include_archive else []
            curr_exercises: list[Exercise] = self.get_exercises(et)

            for ex in arch_exercises:
                if ex.is_in_future() and self.__is_client_already_in_exercise(client, ex, True):
                    appointmens.append(Appointment(client, ex))
            for ex in curr_exercises:
                if ex.is_in_future() and self.__is_client_already_in_exercise(client, ex, False):
                    appointmens.append(Appointment(client, ex))
        return appointmens

    def delete_appointment(self, appointment: Appointment) -> bool:
        row_num: int = self.__find_client_position_in_exersise(appointment.get_client(), appointment.get_exercise(), False)
        if row_num > 0:
            self.__delete_client_from_exercise(appointment.get_exercise().get_type(), row_num)
            return True
        return False

    def __get_worksheet(self, ws_title: str) -> Worksheet:
        if ws_title not in self.__worksheets_cache.keys():
            return None
        else:
            return self.__worksheets_cache[ws_title]

    def __add_client_in_exercise(self, appointment: Appointment):
        ws = self.__get_worksheet(appointment.get_exercise().get_type().get_name())
        if ws is None:
            appointment.set_status(Appointment.Status.NOTFOUND)
            return
        if not appointment.get_exercise().is_in_future():
            appointment.set_status(Appointment.Status.EXERCISE_IN_PAST)
            return
        if self.__is_client_already_in_exercise(appointment.get_client(), appointment.get_exercise(), False):
            appointment.set_status(Appointment.Status.ALREADY_ADDED)
            return
        row_num = self.__find_row_for_client_in_execise(appointment)
        if row_num == 0:
            appointment.set_status(Appointment.Status.GROUPFULL)
            return
        self.__write_client_in_exercise(appointment, ws, row_num)
        if row_num >= appointment.get_exercise().get_start_reserve_row():
            appointment.set_reserved_capacity()
        appointment.set_status(Appointment.Status.SUCCESS)

    def __find_client_position_in_exersise(self, client: Client, exercise: Exercise, is_archive: bool) -> int:
        ws_name: str = self.__archive_sheet_name(exercise.get_type().get_name()) if is_archive else exercise.get_type().get_name()
        # check in main capacity
        for r in range(exercise.get_capacity_start_row(), exercise.get_capacity_end_row() + 1):
            client_phone = self.__get_val(ws_name, r, 3)
            if client_phone == client.get_phone():
                return r
        # check in extended capacity
        for r in range(exercise.get_start_reserve_row(), exercise.get_end_reserve_row() + 1):
            client_phone = self.__get_val(ws_name, r, 3)
            if client_phone == client.get_phone():
                return r
        return 0

    def __is_client_already_in_exercise(self, client: Client, exercise: Exercise, is_archive: bool) -> bool:
        return 0 < self.__find_client_position_in_exersise(client, exercise, is_archive)

    def __delete_client_from_exercise(self, exercise_type: ExerciseType, row_num: int):
        ws: Worksheet = self.__get_worksheet(exercise_type.get_name())
        cells: list[Cell] = []
        col_num: int = 2
        cells.append(Cell(row_num, col_num, ''))
        col_num += 1
        cells.append(Cell(row_num, col_num, ''))
        if exercise_type.is_size_foot_required():
            col_num += 1
            cells.append(Cell(row_num, col_num, ''))
        ws.update_cells(cells)
        self.__invalidate_cache(exercise_type.get_name())

    def __write_client_in_exercise(self, appointment: Appointment, ws: Worksheet, row_num: int):
        cells: list[Cell] = []
        col_num: int = 2
        cells.append(Cell(row_num, col_num, appointment.get_client().get_name()))
        col_num += 1
        cells.append(Cell(row_num, col_num, appointment.get_client().get_phone()))
        col_num += 1
        fs = appointment.get_client().get_foot_size()
        if fs > 0 and appointment.get_exercise().get_type().is_size_foot_required():
            cells.append(Cell(row_num, col_num, fs))
        ws.update_cells(cells)
        self.__invalidate_cache(appointment.get_exercise().get_type().get_name())

    def __find_row_for_client_in_execise(self, appointment: Appointment) -> int:
        self.__invalidate_cache(appointment.get_exercise().get_type().get_name())
        self.__cache_worksheet(appointment.get_exercise().get_type().get_name())
        # take a row_num that the Exercise object knows
        usr_col: int = 3
        row_num = 0
        while row_num < appointment.get_exercise().get_end_reserve_row():
            row_num = appointment.get_exercise().get_row_first_free_slot()
            current_value = self.__get_val(appointment.get_exercise().get_type().get_name(), row_num, usr_col)
            if current_value != "":
                appointment.get_exercise().take_a_slot()
            else:
                return row_num
        return 0

    def __cache_worksheet_names(self):
        worksheets: list[Worksheet] = self.__sh.worksheets()
        self.__worksheets_cache = {}  # reset cache
        for ws in worksheets:
            if self.__is_valid_worksheet_for_cache(ws.title):
                self.__worksheets_cache[ws.title] = ws

    def __cache_worksheet(self, ws_name: str):
        if ws_name not in self.__worksheets_cache.keys():
            return
        if self.__is_cache_valid(ws_name):
            return
        ws: Worksheet = self.__worksheets_cache[ws_name]
        ex_type: ExerciseType = ExerciseType(self.__original_exercise_name(ws_name), self.__config_sheet)
        first_col = self.__first_col_exercises
        last_col = self.__last_col_exercises
        max_row = ex_type.num_rows_in_worksheet()
        if ws_name.startswith(self.__archive_current_week_prefix()):
            max_row *= 2
        self.__data_cache[ws_name] = ws.get(f"{first_col}1:{last_col}{max_row}")
        self.__validate_cache(ws_name)

    def __get_val(self, ws_name: str, row: int, col: int):
        try:
            return self.__data_cache[ws_name][row - 1][col - 1]
        except:
            return ''

    def __is_day_to_refresh_schedule(self) -> bool:
        today_date = datetime.now()
        if today_date.weekday() not in self.__days_to_refresh_schedule:
            return False
        col_num: int = 1
        row_num: int = 2
        for ex in ExerciseType.get_type_names():
            ws: Worksheet = self.__sh.worksheet(ex)
            value = ws.cell(row_num, col_num).value
            if value is not None:
                value = self.__parse_date(value)
            if value is not None:
                return (today_date - value).days >= self.__days_of_expiration_to_trigger_schedule_refresh
        return False

    def __refresh_schedule(self):
        if self.__is_day_to_refresh_schedule():
            self.__archive_old_week()
            self.__create_new_week()
            self.__cache_worksheet_names()

    def __archive_old_week(self):
        for ws in self.__worksheets_cache:
            if self.__is_worksheet_exercise_type(ws):
                archive_name: str = self.__archive_sheet_name(ws)
                self.__worksheets_cache[ws].update_title(archive_name)

    def __create_new_week(self):
        worksheets: list[Worksheet] = self.__sh.worksheets()
        new_sheet_idx: int = 1
        for ws in worksheets:
            if ws.title.startswith(self.__template_sheet_prefix):
                ws_name: str = ws.title.removeprefix(self.__template_sheet_prefix)
                if self.__is_worksheet_exercise_type(ws_name):
                    self.__sh.duplicate_sheet(ws.id, new_sheet_name=ws_name, insert_sheet_index=new_sheet_idx)
                    new_sheet_idx += 1
        worksheets = self.__sh.worksheets()
        self.__config_sheet.invalidate_cache()
        self.__config_sheet.refresh_cache()
        for ws in worksheets:
            if self.__is_worksheet_exercise_type(ws.title):
                ex_type: ExerciseType = ExerciseType(ws.title, self.__config_sheet)
                cells: list[Cell] = []
                for i in range(0, ex_type.exercise_count()):
                    row_num: int = ex_type.get_exercise_row(i)
                    title: tuple[str, str, str] = ex_type.get_exercise_title(i)
                    col_num: int = 1
                    for j in range(0, 3):
                        cells.append(Cell(row_num, j + col_num, title[j]))
                ws.update_cells(cells)
            self.__invalidate_cache(ws.title)

    def __parse_date(self, value: str) -> datetime:
        date_strings: list[str] = value.split('.')
        try:
            return datetime(int(date_strings[2]), int(date_strings[1]), int(date_strings[0]))
        except:
            return None

    def __current_week_num(self) -> int:
        today = datetime.now()
        return today.isocalendar()[1]

    def __archive_current_week_prefix(self) -> str:
        today = datetime.now()
        return f"{self.__archive_sheet_prefix}{self.__current_week_num()}-{today.year} "

    def __archive_sheet_name(self, ex_type_name: str) -> str:
        return f"{self.__archive_current_week_prefix()}{ex_type_name}"

    def __original_exercise_name(self, arch_name: str) -> str:
        if not arch_name.startswith(self.__archive_current_week_prefix()):
            return arch_name
        return arch_name.removeprefix(self.__archive_current_week_prefix())

    def __validate_cache(self, ws_name: str):
        self.__cache_is_fresh[ws_name] = True

    def __invalidate_cache(self, ws_name: str):
        self.__cache_is_fresh[ws_name] = False

    def __is_cache_valid(self, ws_name: bool) -> bool:
        if ws_name not in self.__cache_is_fresh.keys():
            self.__cache_is_fresh[ws_name] = False
        return self.__cache_is_fresh[ws_name]
