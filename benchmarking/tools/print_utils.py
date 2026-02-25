import datetime


def print_green(text):
    print(f"\033[32m{text}\033[0m")


def print_red(text):
    print(f"\033[31m{text}\033[0m")


def print_yellow(text):
    print(f"\033[33m{text}\033[0m")


def print_purple(text):
    print(f"\033[35m{text}\033[0m")


def print_finish(text):
    print_cyan(f"{text}, {datetime.datetime.now().strftime("%H:%M:%S")}\n")


def print_start(text):
    print_cyan(f"{text}, {datetime.datetime.now().strftime("%H:%M:%S")}")


def print_orange(text):
    print(f"\033[33;1m{text}\033[0m")  # bright yellow as orange


def print_cyan(text):
    print(f"\033[36m{text}\033[0m")


def print_time_delay(text, timedelta):
    future_time = datetime.datetime.now() + timedelta
    fut_time_str = future_time.strftime("%H:%M:%S")
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{text}, now {time_now}, future {fut_time_str}.")
