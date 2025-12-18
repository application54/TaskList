# Модуль шифрования паролей

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Класс управления шифрованием
class SecurityManager:

    # Инициализация менеджера безопасности
    def __init__(self):
        self.salt = b"securepass_salt_2025_"

    # Шифрование данных
    def encrypt(self, data: str, password: str) -> str:
        try:
            key = self._derive_key(password)
            cipher = Fernet(key)
            encrypted = cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            print(f"Ошибка шифрования: {e}")
            return ""

    # Дешифрование данных
    def decrypt(self, encrypted_data: str, password: str) -> str:
        try:
            key = self._derive_key(password)
            cipher = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ""

    # Генерация ключа шифрования
    def _derive_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))