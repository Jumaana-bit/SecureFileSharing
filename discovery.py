from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, ServiceStateChange
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QListWidgetItem
import socket
import os

class PeerDiscovery(QObject):
    # Define a custom signal to notify the UI when peers are updated
    peers_updated = pyqtSignal(list)

    def __init__(self, device_list_widget):
        super().__init__()
        self.zeroconf = Zeroconf()
        self.service_type = "_securefileshare._tcp.local."
        # Append the process ID to make the service name unique
        self.service_name = f"SecureFileShare-{socket.gethostname()}-{os.getpid()}._securefileshare._tcp.local."
        self.port = self.get_available_port()
        self.peers = []  # List to store discovered peers
        self.deviceList = device_list_widget  # Assign UI component here
        print(f"Device List Widget Passed: {self.deviceList}")  # Debugging
        print(f"Service Name: {self.service_name}")  # Debugging

    def get_available_port(self):
        """Find an available port for the service"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            return s.getsockname()[1]

    def register_service(self):
        """Announces this device as a file-sharing peer"""
        service_info = ServiceInfo(
            self.service_type,
            self.service_name,
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=self.port
        )
        self.zeroconf.register_service(service_info)
        print(f"✅ Service registered: {self.service_name} at port {self.port}")

    def discover_peers(self):
        """Continuously listens for other devices offering the same service."""
        def on_service_state_change(zeroconf, service_type, name, state_change):
            print(f"⚡ Service State Change Detected: {name} -> {state_change}")

            # Ignore the app's own service
            if name == self.service_name:
                print("Ignoring self...")  # Debugging
                return

            if state_change == ServiceStateChange.Removed:
                self.peers = [peer for peer in self.peers if peer["name"] != name]
                print(f"❌ Removed peer: {name}")
            else:
                info = zeroconf.get_service_info(service_type, name)
                if info:
                    peer_ip = socket.inet_ntoa(info.addresses[0])
                    peer_port = info.port
                    print(f"🔍 Found Peer: {name} @ {peer_ip}:{peer_port}")
                    peer_data = {"name": name, "ip": peer_ip, "port": peer_port}

                    # Check if the peer already exists
                    if not any(peer["name"] == name for peer in self.peers):
                        self.peers.append(peer_data)
                        print(f"✅ Peer Added: {self.peers}")
                        print("Calling update_peer_list_ui...")  # Debugging
                        self.peers_updated.emit(self.peers)  # Emit the signal

        browser = ServiceBrowser(self.zeroconf, self.service_type, handlers=[on_service_state_change])

    def stop(self):
        """Cleans up when exiting"""
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()