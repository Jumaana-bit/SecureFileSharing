from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel, QListWidgetItem, QDialog
from PyQt6.QtCore import QTimer
import sys
import threading
from discovery import PeerDiscovery
from transfer import FileTransfer
from login import LoginDialog, ROLES, users  # Import from login.py

class FileShareApp(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.user_role = users.get(username, {}).get("role", "Guest")  # Default to Guest
        self.initUI()
        self.discovery = PeerDiscovery(self.deviceList)
        self.file_transfer = FileTransfer()

        # Connect the peers_updated signal to the update_ui slot
        self.discovery.peers_updated.connect(self.update_ui)

        print(f"📡 Available peers: {self.discovery.peers}")

        self.start_peer_discovery()
        self.start_file_receiver()

    def has_permission(self, permission):
        """Check if the user has the required permission."""
        return permission in ROLES.get(self.user_role, [])

    def initUI(self):
        self.setWindowTitle("Secure File Sharing")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Available Devices:", self)
        layout.addWidget(self.label)

        self.deviceList = QListWidget(self)
        layout.addWidget(self.deviceList)

        self.selectFileButton = QPushButton("Select File", self)
        self.selectFileButton.clicked.connect(self.selectFile)
        layout.addWidget(self.selectFileButton)

        self.sendFileButton = QPushButton("Send File", self)
        self.sendFileButton.setEnabled(False)  # Disabled until a file is selected
        self.sendFileButton.clicked.connect(self.sendFile)
        layout.addWidget(self.sendFileButton)

        self.setLayout(layout)

    def selectFile(self):
        """Opens file dialog to select a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.selectedFile = file_path
            self.sendFileButton.setEnabled(True)
            self.sendFileButton.setText(f"Send: {file_path.split('/')[-1]}")

    def sendFile(self):
        """Sends the selected file to the chosen peer"""
        if not self.has_permission("send_file"):
            print("Permission denied: You do not have permission to send files.")
            return

        selected_peer = self.deviceList.currentItem()
        if selected_peer:
            peer_info = selected_peer.text()
            try:
                # Extract IP and port from the peer info string
                ip_port = peer_info.split(":")[-2:]  # Get the last two parts ("ip:port")
                peer_ip = ip_port[0].strip()  # Extract IP
                peer_port = int(ip_port[1].strip())  # Extract port and convert to integer
                print(f"Sending file to {peer_ip}:{peer_port}")  # Debugging
                threading.Thread(target=self.file_transfer.send_file, args=(self.selectedFile, peer_ip, peer_port)).start()
            except Exception as e:
                print(f"Error parsing peer info: {e}")
        else:
            print("No peer selected.")  # Debugging

    def start_file_receiver(self):
        """Starts a thread to listen for incoming file transfers"""
        if not self.has_permission("receive_file"):
            print("Permission denied: You do not have permission to receive files.")
            return

        threading.Thread(target=self.file_transfer.receive_file, args=(self.discovery.port,), daemon=True).start()

    def update_ui(self, peers):
        """Slot to update the UI with the latest peers"""
        print("Updating UI...")  # Debugging
        self.deviceList.clear()  # Clear the list
        for peer in peers:
            peer_info = f"{peer['name']} : {peer['ip']}:{peer['port']}"
            print(f"Adding peer to UI: {peer_info}")  # Debugging
            self.deviceList.addItem(QListWidgetItem(peer_info))  # Add items properly

    def start_peer_discovery(self):
        """Starts peer discovery in a separate thread to avoid freezing the UI"""
        self.discovery.register_service()
        threading.Thread(target=self.discovery.discover_peers, daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        username = login_dialog.username_input.text()
        window = FileShareApp(username)
        window.show()
        sys.exit(app.exec())