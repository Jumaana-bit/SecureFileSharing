import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

logging.basicConfig(
    filename="file_share_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ROLES = {
    "Admin": ["send_file", "receive_file", "discover_peers", "manage_users"],
    "User": ["send_file", "receive_file", "discover_peers"],
    "Guest": ["receive_file"]
}

users = {
    "admin_user": {"password": "admin123", "role": "Admin"},
    "regular_user": {"password": "user123", "role": "User"},
    "guest_user": {"password": "guest123", "role": "Guest"}
}

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)  # Increased height for new button

        layout = QVBoxLayout()

        # Username and password fields
        self.username_label = QLabel("Username:", self)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:", self)
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Guest login button
        self.guest_button = QPushButton("Continue as Guest", self)
        self.guest_button.clicked.connect(self.guest_login)
        layout.addWidget(self.guest_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in users and users[username]["password"] == password:
            role = users[username]["role"]
            logging.info(f"User {username} ({role}) logged in successfully.")
            self.accept()
        else:
            print("Invalid username or password.")

    def guest_login(self):
        self.username_input.setText("guest_user")
        self.password_input.setText("guest123")
        logging.info("Guest user logged in")
        self.accept()