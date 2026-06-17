import bcrypt

from app.modules.users.exceptions import InvalidPassError, SamePasswordsError


def hash_pass(password: str) -> str:
    salt = bcrypt.gensalt()
    pass_hash = bcrypt.hashpw(password.encode(), salt)

    return pass_hash.decode()


def verify_pass(password: str, password_hash: str) -> None:
    if not bcrypt.checkpw(password.encode(), password_hash.encode()):
        raise InvalidPassError('Password not verified (invalid data)')


def same_pass(password: str, password_hash: str) -> None:
    if bcrypt.checkpw(password.encode(), password_hash.encode()):
        raise SamePasswordsError('Old password == new password error')
