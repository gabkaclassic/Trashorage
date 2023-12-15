from cryptography.fernet import Fernet
from settings import encrypt_key


class Cipher:
    cipher = Fernet(encrypt_key)
    encoding = 'utf-8'

    @staticmethod
    def encrypt(value: str):
        return Cipher.cipher.encrypt(
            bytes(value, Cipher.encoding)
        )

    @staticmethod
    def decrypt(value: str):
        return Cipher.cipher.decrypt(
            bytes(value, Cipher.encoding)
        ).decode(Cipher.encoding)
