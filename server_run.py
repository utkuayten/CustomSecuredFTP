from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Create a user with username and password
authorizer = DummyAuthorizer()

# Replace with the cloud root.
ftp_root = "C:/Users/Utku Ayten/Desktop/ftp_root"
authorizer.add_user("user", "12345", ftp_root, perm="elradfmw")

# Set up the FTP handler
handler = FTPHandler
handler.authorizer = authorizer

# Define the server and its port
server = FTPServer(("0.0.0.0", 2121), handler)

print("FTP Server running on port 2121...")
# Start the server
server.serve_forever()