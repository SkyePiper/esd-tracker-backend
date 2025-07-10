"""Utilities for the passwords"""

from passlib.context import CryptContext

password_context = CryptContext(schemes=["scrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain password matches a hashed password

    :param plain_password: The plain password
    :param hashed_password: The hashed password
    :return: Whether they match
    """

    return password_context.verify(plain_password, hashed_password)


async def hash_password(password: str) -> str:
    """Hashes a password

    :param password: The password to hash
    :return: The hashed password
    """

    return password_context.hash(password)
