from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import json
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
import base64

# Paths
BASE_DIR = os.path.dirname(__file__)
USER_DB = os.path.join(BASE_DIR, "db/users.json")
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "keys/private_key.pem")


def initialize_database():
    """Ensure the users database is initialized."""
    db_dir = os.path.dirname(USER_DB)
    os.makedirs(db_dir, exist_ok=True)  # Ensure the db directory exists
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f, indent=4)  # Initialize with an empty dictionary
        print(f"Database created at {USER_DB}")


def load_users():
    """Load user data from the database."""
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("User database not found. Initializing a new one.")
        initialize_database()
        return {}


def save_users(users):
    """Save user data to the database."""
    os.makedirs(os.path.dirname(USER_DB), exist_ok=True)  # Ensure the database directory exists
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)


def initialize_users(authorizer):
    """Initialize all users from the database into the authorizer."""
    users = load_users()
    for username, info in users.items():
        try:
            authorizer.add_user(
                username,
                info["password"],
                info["home_dir"],
                perm="elradfmw"  # Full permissions
            )
            print(f"User initialized: {username}")
        except Exception as e:
            print(f"Error initializing user {username}: {e}")


def decrypt_password(encrypted_password):
    """Decrypt the encrypted password using the private key."""
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)
    return private_key.decrypt(
        encrypted_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()  # Decode to plaintext string


def encrypt_with_public_key(public_key_pem, data):
    public_key = load_pem_public_key(public_key_pem.encode("utf-8"))

    # Encrypt the data
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data


def encrypt_file_with_public_key(public_key_pem, file_path, output_path):
    """
    Encrypt a file using the user's public key.
    Args:
        public_key_pem (str): PEM-encoded public key.
        file_path (str): Path to the file to encrypt.
        output_path (str): Path to save the encrypted file.
    """
    # Load the public key
    public_key = load_pem_public_key(public_key_pem.encode("utf-8"))

    # Generate a random AES key
    aes_key = os.urandom(32)  # 256-bit AES key
    iv = os.urandom(16)  # Initialization vector

    # Encrypt the AES key with the public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encrypt the file with the AES key
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()

    with open(file_path, "rb") as f_in, open(output_path, "wb") as f_out:
        f_out.write(encrypted_aes_key)  # Write encrypted AES key
        f_out.write(iv)  # Write IV
        f_out.write(encryptor.update(f_in.read()) + encryptor.finalize())  # Write encrypted file content


def decrypt_file_with_private_key(private_key_path, encrypted_file_path, output_path):
    """
    Decrypt a file using the server's private key.
    Args:
        private_key_path (str): Path to the private key.
        encrypted_file_path (str): Path to the encrypted file.
        output_path (str): Path to save the decrypted file.
    """
    # Load the private key
    with open(private_key_path, "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)

    with open(encrypted_file_path, "rb") as f_in:
        # Read encrypted AES key and IV
        encrypted_aes_key = f_in.read(256)  # Assuming 2048-bit RSA key
        iv = f_in.read(16)

        # Decrypt the AES key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the file content with the AES key
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()

        with open(output_path, "wb") as f_out:
            f_out.write(decryptor.update(f_in.read()) + decryptor.finalize())


class CustomFTPHandler(FTPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add the REGISTER, LOGIN, and UPDATE_PUBLIC_KEY commands
        self.proto_cmds["REGISTER"] = dict(perm=None, auth=False, arg=True)
        self.proto_cmds["LOGIN"] = dict(perm=None, auth=False, arg=True)
        self.proto_cmds["UPDATE_PUBLIC_KEY"] = dict(perm=None, auth=False, arg=True)

    def ftp_REGISTER(self, username_password):
        """Custom REGISTER command to create a new user."""
        print(f"REGISTER Command received: {username_password}")

        try:
            # Parse the username and hashed password
            username, hashed_password = username_password.split(" ", 1)
        except ValueError:
            self.respond("500 Syntax error. Usage: REGISTER <username> <hashed_password>")
            return

        users = load_users()

        if username in users:
            self.respond("550 User already exists.")
            return

        # Define the user's home directory
        home_dir = os.path.join(BASE_DIR, f"root/{username}")
        os.makedirs(home_dir, exist_ok=True)

        # Save the user in the database
        users[username] = {"password": hashed_password, "home_dir": home_dir}
        save_users(users)

        # Add the user dynamically to the authorizer
        try:
            self.authorizer.add_user(username, hashed_password, home_dir, perm="elradfmw")
            print(f"User registered and added: {username}")
            self.respond("200 User registered successfully.")
        except Exception as e:
            print(f"Error adding user to authorizer: {e}")
            self.respond("550 Internal server error. Please try again.")

    def ftp_LOGIN(self, username_password):
        """Custom LOGIN command to authenticate a user."""
        print(f"LOGIN Command received: {username_password}")

        try:
            # Parse the username and encrypted password
            username, encrypted_password_hex = username_password.split(" ", 1)
            print(f"Parsed Username: {username}")
            print(f"Encrypted Password (Hex): {encrypted_password_hex}")

            # Convert hex to bytes
            encrypted_password = bytes.fromhex(encrypted_password_hex)

            # Decrypt the password using the private key
            decrypted_password = decrypt_password(encrypted_password)
            print(f"Decrypted Password: {decrypted_password}")

            # Load users and verify credentials
            users = load_users()
            if username in users:
                stored_password = users[username]["password"]
                if stored_password == decrypted_password:
                    print(f"User '{username}' authenticated successfully.")

                    # Mark session as authenticated
                    self.authenticated = True
                    self.username = username

                    # Set up the user's file system and session
                    user_home = users[username]["home_dir"]
                    self.fs = self.abstracted_fs(user_home, self)

                    # Call on_login to complete login flow
                    self.on_login(username)

                    self.respond("230 Login successful.")
                else:
                    print(f"Password mismatch for user '{username}'.")
                    self.respond("530 Login incorrect.")
            else:
                print(f"User '{username}' not found in the user database.")
                self.respond("530 Login failed. User not found.")

        except Exception as e:
            print(f"Error during LOGIN: {e}")
            self.respond("530 Login failed due to an internal server error.")

    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    import base64

    def ftp_UPDATE_PUBLIC_KEY(self, username_key_iv):
        """Custom command to update the public key for a user."""
        print("User public key received")
        try:
            # Split the payload into components
            username, rsa_encrypted_aes_key_hex, aes_encrypted_data_hex, iv_hex = username_key_iv.split(" ", 3)

            # Convert hex to bytes
            rsa_encrypted_aes_key = bytes.fromhex(rsa_encrypted_aes_key_hex)
            aes_encrypted_data = bytes.fromhex(aes_encrypted_data_hex)
            iv = bytes.fromhex(iv_hex)

            # Load the server's private key
            with open("keys/private_key.pem", "rb") as key_file:
                private_key = load_pem_private_key(key_file.read(), password=None)

            # Decrypt the AES key using the server's private key
            aes_key = private_key.decrypt(
                rsa_encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print(f"Decrypted AES Key: {aes_key.hex()}")  # Debugging

            # Decrypt the AES-encrypted public key using the decrypted AES key
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            decrypted_public_key = decryptor.update(aes_encrypted_data) + decryptor.finalize()
            print(f"Decrypted Public Key (Raw Bytes): {decrypted_public_key}")  # Debugging

            # Decode the decrypted public key (Base64-decoded back to PEM format)
            try:
                public_key_pem = base64.b64decode(decrypted_public_key).decode("utf-8")
            except Exception as e:
                print(f"Error decoding Base64 or UTF-8: {e}")
                self.respond("550 Decrypted public key is invalid.")
                return

            # Load the existing users
            users = load_users()

            if username not in users:
                self.respond("550 User not found.")
                return

            # Save the public key for the user in the database
            users[username]["public_key"] = public_key_pem
            save_users(users)

            print(f"Public key updated for user: {username}")
            self.respond("200 Public key updated successfully.")

        except Exception as e:
            print(f"Error updating public key for user: {e}")
            self.respond("550 Internal server error.")

    def ftp_SEND_SECURE_MESSAGE(self, username_message):
        """Send a secure message encrypted with the user's public key."""
        print("SEND_SECURE_MESSAGE Command received.")
        try:
            # Parse the username and the message
            username, message = username_message.split(" ", 1)

            # Load the user's public key from the database
            users = load_users()
            if username not in users:
                self.respond("550 User not found.")
                return

            public_key_pem = users[username].get("public_key")
            if not public_key_pem:
                self.respond("550 Public key not found for user.")
                return

            # Encrypt the message with the user's public key
            encrypted_message = encrypt_with_public_key(public_key_pem, message.encode("utf-8"))

            # Convert encrypted message to Base64 for transmission
            encrypted_message_b64 = base64.b64encode(encrypted_message).decode("utf-8")

            # Send the encrypted message
            self.respond(f"200 Encrypted message: {encrypted_message_b64}")
            print(f"Secure message sent to {username}: {encrypted_message_b64}")
        except Exception as e:
            print(f"Error sending secure message: {e}")
            self.respond("550 Internal server error.")

        def ftp_ENCRYPTED_DOWNLOAD(self, username_file):
            """Encrypt and send a file to the client."""
            print("ENCRYPTED_DOWNLOAD Command received.")
            try:
                # Parse the username and file path
                username, file_path = username_file.split(" ", 1)

                # Load user's public key
                users = load_users()
                if username not in users or "public_key" not in users[username]:
                    self.respond("550 User not found or public key missing.")
                    return

                public_key_pem = users[username]["public_key"]

                # Encrypt the file with the user's public key
                encrypted_file_path = f"{file_path}.enc"
                encrypt_file_with_public_key(public_key_pem, file_path, encrypted_file_path)

                # Send the encrypted file to the client
                self.respond(f"150 Opening binary mode data connection for {encrypted_file_path}.")
                with open(encrypted_file_path, "rb") as f:
                    self.dtp_send(f.read())
                self.respond("226 Transfer complete.")
                os.remove(encrypted_file_path)  # Clean up temporary file
            except Exception as e:
                print(f"Error during ENCRYPTED_DOWNLOAD: {e}")
                self.respond("550 Encrypted download failed.")

        def ftp_ENCRYPTED_UPLOAD(self, username_file):
            """Receive and decrypt an encrypted file from the client."""
            print("ENCRYPTED_UPLOAD Command received.")
            try:
                # Parse the username and file path
                username, file_path = username_file.split(" ", 1)

                # Receive the encrypted file from the client
                self.respond(f"150 Opening binary mode data connection for {file_path}.enc.")
                encrypted_file_path = f"{file_path}.enc"
                with open(encrypted_file_path, "wb") as f:
                    f.write(self.dtp_recv())
                self.respond("226 Transfer complete.")

                # Decrypt the file with the server's private key
                decrypted_file_path = file_path
                decrypt_file_with_private_key(PRIVATE_KEY_PATH, encrypted_file_path, decrypted_file_path)
                os.remove(encrypted_file_path)  # Clean up temporary file
            except Exception as e:
                print(f"Error during ENCRYPTED_UPLOAD: {e}")
                self.respond("550 Encrypted upload failed.")


if __name__ == "__main__":
    # Ensure the database is initialized
    initialize_database()

    # Initialize the authorizer
    authorizer = DummyAuthorizer()

    # Load existing users into the authorizer
    initialize_users(authorizer)

    # Assign the custom handler to the authorizer
    handler = CustomFTPHandler
    handler.authorizer = authorizer

    # Start the FTP server
    server = FTPServer(("0.0.0.0", 2121), handler)
    print("FTP server running on 0.0.0.0:2121...")
    server.serve_forever()
