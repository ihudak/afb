from WeekDayTranslator import WeekDayTranslator
from ConfigSheet import ConfigSheet
from datetime import datetime
from datetime import timedelta


class ExerciseType:
    __exersise_types_parameters = {
        'KANGOO JUMPS': {
            'capacity': 15,
            'reserved_capacity': 3,
            'foot_size_required': True,
            'schedule': {
                'Mon': ['12:00', '19:30'],
                'Tue': ['20:30'],
                'Wed': ['12:00', '19:30'],
                'Thu': ['19:30', '20:30'],
                'Fri': [],
                'Sat': ['12:00'],
                'Sun': []
            }
        },
        'Силова FULL BODY': {
            'capacity': 18,
            'reserved_capacity': 3,
            'foot_size_required': False,
            'schedule': {
                'Mon': ['18:30'],
                'Tue': ['10:40'],
                'Wed': [],
                'Thu': ['10:30', '17:30', '18:30'],
                'Fri': ['18:30'],
                'Sat': ['9:00', '10:00'],
                'Sun': []
            }
        },
        'Розтяжка STRETCHING': {
            'capacity': 15,
            'reserved_capacity': 3,
            'foot_size_required': False,
            'schedule': {
                'Mon': [],
                'Tue': ['11:40', '18:30'],
                'Wed': ['20:30'],
                'Thu': [],
                'Fri': [],
                'Sat': ['11:00'],
                'Sun': []
            }
        },
        'TRX': {
            'capacity': 18,
            'reserved_capacity': 3,
            'foot_size_required': False,
            'schedule': {
                'Mon': ['10:30', '17:30', '20:30'],
                'Tue': ['19:30'],
                'Wed': ['10:30', '17:30', '18:30'],
                'Thu': [],
                'Fri': ['10:30', '20:30'],
                'Sat': [],
                'Sun': ['11:00', '12:00']
            }
        }
    }

    def __init__(self, name: str, config_sheet: ConfigSheet = None):
        self.__name: str = name
        if config_sheet is not None:
            conf = config_sheet.get_configs()
            if conf is not None:
                ExerciseType.__exersise_types_parameters = conf
        if name in ExerciseType.__exersise_types_parameters.keys():
            params = ExerciseType.__exersise_types_parameters[name]
            self.__size_foot_required: bool = params['foot_size_required']
            self.__capacity: int = params['capacity']
            self.__reserve_capacit: int = params['reserved_capacity']
        else:
            self.__size_foot_required: bool = False
            self.__capacity: int = 0
            self.__reserve_capacit: int = 0

    @classmethod
    def get_type_names(cls) -> list[str]:
        return ExerciseType.__exersise_types_parameters.keys()

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        return name in ExerciseType.__exersise_types_parameters.keys()

    def is_valid(self) -> bool:
        return self.get_name() in ExerciseType.__exersise_types_parameters.keys()

    def get_name(self) -> str:
        return self.__name

    def is_size_foot_required(self) -> bool:
        return self.__size_foot_required

    def get_capacity(self) -> int:
        return self.__capacity

    def get_reserve_capacity(self) -> int:
        return self.__reserve_capacit

    def __get_config(self) -> {str, dict}:
        return ExerciseType.__exersise_types_parameters[self.get_name()]

    def exercise_count(self) -> int:
        count: int = 0
        config: {str, dict} = self.__get_config()
        for c in config['schedule']:
            count += len(config['schedule'][c])
        return count

    def get_exercise_row(self, num_exercise: int) -> int:
        if num_exercise > self.exercise_count() or num_exercise < 0:
            return 0
        config: {str, dict} = self.__get_config()
        return 2 + num_exercise * (config['capacity'] + config['reserved_capacity'] + 3 + 3)

    def get_exercise_title(self, num_exercise: int) -> tuple[str, str, str]:
        config: {str, dict} = self.__get_config()
        for schedule in config['schedule']:
            if num_exercise >= len(config['schedule'][schedule]):
                num_exercise -= len(config['schedule'][schedule])
            else:
                sch = config['schedule'][schedule][num_exercise]
                today: datetime = datetime.now()
                next_sunday = today if today.weekday() == 6 else self.next_weekday(today, 6)
                scheduled_day = self.next_weekday(next_sunday, WeekDayTranslator.translate_num(schedule))
                return (scheduled_day.strftime("%d.%m.%Y"), sch, WeekDayTranslator.translate_ua(schedule))
        return ('', '', '')

    def num_rows_in_worksheet(self) -> int:
        config: {str, dict} = self.__get_config()
        return self.exercise_count() * (config['capacity'] + config['reserved_capacity'] + 3 + 3) - 2

    def next_weekday(self, d: datetime, weekday: int):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return d + timedelta(days_ahead)
