from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
import sys
import threading
from discovery import PeerDiscovery

class FileShareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.discovery = PeerDiscovery()
        self.start_peer_discovery()

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
        layout.addWidget(self.sendFileButton)

        self.setLayout(layout)

    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.sendFileButton.setEnabled(True)
            self.sendFileButton.setText(f"Send: {file_path.split('/')[-1]}")

    def start_peer_discovery(self):
        """Starts peer discovery in a separate thread to avoid freezing the UI"""
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def discover_peers(self):
        """Updates the UI with discovered peers"""
        self.discovery.register_service()
        self.discovery.discover_peers()
        while True:
            self.deviceList.clear()
            for peer in self.discovery.peers:
                self.deviceList.addItem(peer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileShareApp()
    window.show()
    sys.exit(app.exec())
