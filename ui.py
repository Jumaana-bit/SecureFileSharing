from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
import sys
import threading
from discovery import PeerDiscovery
from transfer import FileTransfer

class FileShareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.discovery = PeerDiscovery()
        self.file_transfer = FileTransfer()
        self.start_peer_discovery()
        self.start_file_receiver()

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
        selected_peer = self.deviceList.currentItem()
        if selected_peer:
            peer_ip = selected_peer.text().split(":")[0]  # Extract IP address
            peer_port = 5000  # Assuming a fixed port
            threading.Thread(target=self.file_transfer.send_file, args=(self.selectedFile, peer_ip, peer_port)).start()

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

    def start_file_receiver(self):
        """Starts a thread to listen for incoming file transfers"""
        threading.Thread(target=self.file_transfer.receive_file, args=(5000,), daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileShareApp()
    window.show()
    sys.exit(app.exec())
