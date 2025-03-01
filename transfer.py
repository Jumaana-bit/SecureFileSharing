import socket
import threading
from security import Security

class FileTransfer:
    def __init__(self):
        self.security = Security()
    
    def send_file(self, file_path, peer_ip, peer_port):
        """Sends an encrypted file to a peer"""
        # Establish a TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer_ip, peer_port))

        # Exchange public keys
        sock.sendall(self.security.public_key.public_bytes())
        peer_public_key_bytes = sock.recv(1024)

        # Generate shared AES key
        aes_key = self.security.generate_shared_key(peer_public_key_bytes)

        # Encrypt and send file
        encrypted_file = self.security.encrypt_file(file_path, aes_key)
        with open(encrypted_file, 'rb') as f:
            sock.sendall(f.read())

        print(f"Sent encrypted file: {encrypted_file}")
        sock.close()

    def receive_file(self, port):
        """Receives and decrypts an encrypted file"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(1)

        print(f"Listening for incoming files on port {port}...")
        conn, addr = server_socket.accept()
        
        # Receive public key
        peer_public_key_bytes = conn.recv(1024)
        conn.sendall(self.security.public_key.public_bytes())

        # Generate shared AES key
        aes_key = self.security.generate_shared_key(peer_public_key_bytes)

        # Receive encrypted file
        with open("received_file.enc", 'wb') as f:
            f.write(conn.recv(4096))

        # Decrypt file
        decrypted_file = self.security.decrypt_file("received_file.enc", aes_key)
        print(f"File received and decrypted: {decrypted_file}")

        conn.close()
