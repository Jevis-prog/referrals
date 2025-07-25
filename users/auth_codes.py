import random
import time
from threading import Lock

_codes = {}
_lock = Lock()


def generate_code() -> str:
    return f"{random.randint(1000, 9999)}"


def send_code(phone_number: int) -> None:
    with _lock:
        code = generate_code()
        _codes[phone_number] = code
    time.sleep(2)
    print(f"Отправлен код {code} на номер {phone_number}")


def verify_code(phone_number: int, code: int) -> bool:
    with _lock:
        correct_code = _codes.get(phone_number)
        if correct_code is not None and correct_code == code:
            del _codes[phone_number]
            return True
    return False
