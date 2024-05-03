import Client
import Exercise
from enum import Enum


class Appointment:
    class Status(Enum):
        NONE = 0
        SUCCESS = 1
        GROUPFULL = 2
        NOTFOUND = 3
        ALREADY_ADDED = 4
        EXERCISE_IN_PAST = 5

    def __init__(self, client: Client, exercise: Exercise):
        self.__client: Client = client
        self.__exercise: Exercise = exercise
        self.__status: Appointment.Status = Appointment.Status.NONE
        self.__main_capacity: bool = True

    def get_client(self) -> Client:
        return self.__client

    def get_exercise(self) -> Exercise:
        return self.__exercise

    def get_status(self) -> Status:
        return self.__status

    def set_status(self, status: Status):
        self.__status = status

    def set_reserved_capacity(self):
        self.__main_capacity = False

    def is_reserved_capacity(self):
        return not self.__main_capacity

    def is_main_capacity(self):
        return self.__main_capacity

    def __str__(self) -> str:
        return f'{self.__exercise.get_type().get_name()} - {self.__exercise.get_timestamp()}'
