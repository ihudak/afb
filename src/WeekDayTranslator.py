class WeekDayTranslator:
    __weekdays_ua: {str, str} = {
        'Mon': 'понеділок',
        'Tue': 'вівторок',
        'Wed': 'середа',
        'Thu': 'четвер',
        'Fri': 'пʼятниця',
        'Sat': 'субота',
        'Sun': 'неділя'
    }

    __weekdays_num: {str, int} = {
        'Mon': 0,
        'Tue': 1,
        'Wed': 2,
        'Thu': 3,
        'Fri': 4,
        'Sat': 5,
        'Sun': 6
    }

    __weekdays: list[str] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    @classmethod
    def translate_ua(cls, weekday: str) -> str:
        if weekday in WeekDayTranslator.__weekdays_ua.keys():
            return WeekDayTranslator.__weekdays_ua[weekday]
        else:
            return ''

    @classmethod
    def translate_num(cls, weekday: str) -> int:
        if weekday in WeekDayTranslator.__weekdays_num.keys():
            return WeekDayTranslator.__weekdays_num[weekday]
        else:
            return -1

    @classmethod
    def translate_str(cls, weekday_num: int) -> str:
        if weekday_num >= len(WeekDayTranslator.__weekdays):
            return ''
        return WeekDayTranslator.__weekdays[weekday_num]
