import time
from functools import wraps
from random import uniform


def backoff(start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: float = 10, max_retries: int = 10, jitter: bool = True):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param max_retries: максимальное количество попыток
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param jitter: если True, добавляет случайное отклонение к времени ожидания
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            while n < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    sleep_time = start_sleep_time * (factor ** n)
                    if sleep_time > border_sleep_time:
                        sleep_time = border_sleep_time

                    if jitter:
                        sleep_time += uniform(-start_sleep_time, start_sleep_time)

                    time.sleep(max(start_sleep_time, sleep_time))
                    n += 1
        return inner

    return func_wrapper
