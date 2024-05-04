from ExerciseType import ExerciseType
from datetime import datetime


class Exercise:
    def __init__(self,
                 type: ExerciseType,
                 exercise_date: str,
                 exercise_time: str,
                 exercise_weekday: str,
                 start_row: int
                 ):
        self.__type: ExerciseType = type
        self.__exercise_date: str = exercise_date
        self.__exercise_time: str = exercise_time
        self.__exercise_weekday: str = exercise_weekday
        self.__free_slots: int = 0
        self.__start_row: int = start_row

    def get_type(self) -> ExerciseType:
        return self.__type

    def get_exercise_date(self) -> str:
        return self.__exercise_date

    def get_exercise_time(self) -> str:
        return self.__exercise_time

    def get_datetime(self) -> datetime:
        date_strings: list[str] = self.__exercise_date.split('.')
        time_strings: list[str] = self.__exercise_time.split(':')
        try:
            exercise_datetime: datetime = datetime(int(date_strings[2]), int(date_strings[1]), int(date_strings[0]), int(time_strings[0]), int(time_strings[1]))
            return exercise_datetime
        except:
            return None

    def is_in_future(self) -> bool:
        current_time = datetime.now()
        exercise_time = self.get_datetime()
        return exercise_time is None or exercise_time > current_time

    def get_exercise_weekday(self) -> str:
        return self.__exercise_weekday

    def get_free_slots(self) -> int:
        return self.__free_slots

    def has_free_slots(self) -> bool:
        return self.is_in_future() and self.__free_slots > 0

    def set_free_slots(self, slots: int):
        self.__free_slots = slots

    def take_a_slot(self):
        self.__free_slots -= 1

    def get_timestamp(self) -> str:
        return f'{self.__exercise_date} {self.__exercise_time} {self.__exercise_weekday}'

    def get_capacity_start_row(self) -> int:
        return self.__start_row + 2

    def get_capacity_end_row(self) -> int:
        return self.get_capacity_start_row() + self.__type.get_capacity() - 1

    def get_start_reserve_row(self) -> int:
        return self.get_capacity_end_row() + 2

    def get_end_reserve_row(self) -> int:
        return self.get_start_reserve_row() + self.__type.get_reserve_capacity() - 1

    def get_first_row(self) -> int:
        return self.__start_row

    def get_last_row(self) -> int:
        return self.get_end_reserve_row()

    def get_row_first_free_slot(self) -> int:
        if self.get_free_slots() <= 0:
            return 0  # no free slots
        elif self.get_free_slots() > self.__type.get_reserve_capacity():
            return self.get_capacity_end_row() - self.get_free_slots() + self.__type.get_reserve_capacity() + 1
        else:
            return self.get_end_reserve_row() - self.get_free_slots() + 1

    def is_right_exercise_for_appointment(self, exercise_type: ExerciseType, timestamp: str) -> bool:
        return self.__type == exercise_type and self.get_timestamp() == timestamp and self.__free_slots > 0
