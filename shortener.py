import secrets
import string

from db import code_exists

ALPHABET = string.ascii_letters + string.digits  # 62 characters
CODE_LENGTH = 6


def generate_code(length=CODE_LENGTH):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_code():
    while True:
        code = generate_code()
        if not code_exists(code):
            return code