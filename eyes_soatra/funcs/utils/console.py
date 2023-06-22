from eyes_soatra.funcs.utils.number import get_percent as __get_percent
from eyes_soatra.constant.classes import colors as __colors
import os as __os

def clear_console():
    __os.system('cls' if __os.name == 'nt' else 'clear')

def print_process(
    iterator,
    total,
    show_process=True,
    prefix='processing ',
    suffix=''
):
    if show_process:
        percent = __get_percent(iterator, total)
        info = f'{__colors.OK_GREEN}{prefix}{percent}%{suffix}{__colors.END_COLOR if iterator >= total else ""}'
        end = '\r' if iterator < total else '\n'

        print(info, end=end)
