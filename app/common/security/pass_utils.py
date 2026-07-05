import bcrypt

from app.modules.auth.exceptions import PassVerifyError


def hash_pass(password: str) -> str:
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt)
    return password_hash.decode()


def verify_pass(password: str, password_hash: str) -> None:
    if not bcrypt.checkpw(password.encode(), password_hash.encode()):
        raise PassVerifyError('Password not verified (unauthorize user error)')
