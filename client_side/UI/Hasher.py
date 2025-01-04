import hashlib


class Hasher:
    @staticmethod
    def generate_salt(username: str) -> str:
        """Generate a salt based on the username."""
        return hashlib.sha256(username.encode('utf-8')).hexdigest()[:16]

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Hash the password using the provided salt."""
        combined = (password + salt).encode('utf-8')
        return hashlib.sha256(combined).hexdigest() 