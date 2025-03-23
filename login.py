from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

# Define roles and their permissions
ROLES = {
    "Admin": ["send_file", "receive_file", "discover_peers", "manage_users"],
    "User": ["send_file", "receive_file", "discover_peers"],
    "Guest": ["discover_peers"]
}

# Example user data
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
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.username_label = QLabel("Username:", self)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:", self)
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in users and users[username]["password"] == password:
            self.accept()  # Close the dialog and return QDialog.Accepted
        else:
            print("Invalid username or password.")