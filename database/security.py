import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
crypter = Fernet(os.getenv("HASH_KEY").encode())


def encrypt_data(data):
    if not data: return None
    return crypter.encrypt(data.encode()).decode()


def decrypt_data(data):
    if not data: return None
    try:
        return crypter.decrypt(data.encode()).decode()
    except Exception:
        return data
