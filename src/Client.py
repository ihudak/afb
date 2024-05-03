class Client:
    def __init__(self, id: str, first_name: str, last_name: str, phone: str):
        self.__id: str = id
        self.__first_name: str = first_name
        self.__last_name: str = last_name
        self.__phone: str = phone
        if self.__phone.startswith('+'):
            self.__phone = self.__phone.removeprefix('+')
        self.__status_created: bool = False
        self.__foot_size: int = 0

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return f'{self.__first_name} {self.__last_name}'

    def get_first_name(self) -> str:
        return self.__first_name

    def get_last_name(self) -> str:
        return self.__last_name

    def get_phone(self) -> str:
        return self.__phone

    def get_foot_size(self) -> int:
        return self.__foot_size

    def set_foot_size(self, foot_size: int):
        self.__foot_size = foot_size

    def is_created(self) -> bool:
        return self.__status_created

    def set_created(self):
        self.__status_created = True

    def reset_created(self):
        self.__status_created = False

    def __str__(self) -> str:
        return f'{self.__first_name} {self.__last_name}, phone: {self.__phone}'
