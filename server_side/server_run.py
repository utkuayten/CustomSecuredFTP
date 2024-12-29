from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import json
import os

# Path to the user database
USER_DB = os.path.join(os.path.dirname(__file__), "db/users.json")


def load_users():
    """Load user data from the database."""
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except FileNotFoundError:
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


class CustomFTPHandler(FTPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add the REGISTER command
        self.proto_cmds["REGISTER"] = dict(perm=None, auth=False, arg=True)

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
        home_dir = os.path.join(os.path.dirname(__file__), f"root/{username}")
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


if __name__ == "__main__":
    # Initialize the authorizer
    authorizer = DummyAuthorizer()

    initialize_users(authorizer)

    # Assign the custom handler to the authorizer
    handler = CustomFTPHandler
    handler.authorizer = authorizer

    # Start the FTP server
    server = FTPServer(("127.0.0.1", 2121), handler)
    print("FTP server running on 127.0.0.1:2121...")
    server.serve_forever()
