from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, ServiceStateChange
import socket

class PeerDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.service_type = "_securefileshare._tcp.local."
        self.service_name = f"SecureFileShare-{socket.gethostname()}._securefileshare._tcp.local."
        self.port = 5000  # Default port for file transfers
        self.peers = []

    def register_service(self):
        """Announces this device as a file-sharing peer"""
        service_info = ServiceInfo(
            self.service_type,
            self.service_name,
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=self.port
        )
        self.zeroconf.register_service(service_info)
        print(f"Service registered: {self.service_name}")

    def discover_peers(self):
        """Listens for other devices offering the same service"""
        def on_service_state_change(zeroconf, service_type, name, state_change):
            print(f"State change: {state_change}")  # Debug print to see the attributes
            if state_change == ServiceStateChange.Added:
                print(f"Discovered: {name}")
                self.peers.append(name)

        browser = ServiceBrowser(self.zeroconf, self.service_type, handlers=[on_service_state_change])
        

    def stop(self):
        """Cleans up when exiting"""
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()

if __name__ == "__main__":
    discovery = PeerDiscovery()
    discovery.register_service()
    discovery.discover_peers()
