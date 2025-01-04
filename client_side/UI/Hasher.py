import hashlib
import os
# import socket
# import sslp



class Hasher:
    @staticmethod
    def generate_salt(username: str) -> str:
        """Generate a salt based on the username."""
        salt = hashlib.sha256(username.encode('utf-8')).hexdigest()[:29]
        return salt

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash the password using the provided salt."""
        combined = (password + salt).encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
