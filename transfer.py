import logging
import socket
import threading
from security import Security
from cryptography.hazmat.primitives import serialization  # Add this import

class FileTransfer:
    def __init__(self):
        self.security = Security()
    
    def send_file(self, file_path, peer_ip, peer_port):
        """Sends an encrypted file to a peer"""
        try:
            logging.info(f"Starting file transfer to {peer_ip}:{peer_port}...") 
            print(f"Connecting to {peer_ip}:{peer_port}...")  # Debugging
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            print("Connection established.")  # Debugging

            # Exchange public keys
            print("Exchanging public keys...")  # Debugging
            sock.sendall(self.security.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,  # Use PEM encoding
                format=serialization.PublicFormat.SubjectPublicKeyInfo  # Use SubjectPublicKeyInfo format
            ))
            peer_public_key_bytes = sock.recv(1024)

            # Generate shared AES key
            print("Generating shared AES key...")  # Debugging
            aes_key = self.security.generate_shared_key(peer_public_key_bytes)

            # Encrypt and send file
            print("Encrypting and sending file...")  # Debugging
            encrypted_file = self.security.encrypt_file(file_path, aes_key)
            with open(encrypted_file, 'rb') as f:
                sock.sendall(f.read())

            print(f"Sent encrypted file: {encrypted_file}")
            sock.close()
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_file(self, port=0):  # Port 0 allows OS to choose an available one
        """Continuously receives and decrypts encrypted files."""  
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        server_socket.bind(("0.0.0.0", port))  
        server_socket.listen(5)  # Allows multiple connections  
        print(f"Listening for incoming files on port {server_socket.getsockname()[1]}...")  # Debugging

        while True:  
            conn, addr = server_socket.accept()  
            logging.info(f"Connection established with {addr}. Waiting for file...") 
            print(f"Connected to {addr}")  # Debugging
            threading.Thread(target=self.handle_client, args=(conn,)).start()  

    def handle_client(self, conn):  
        """Handles a single file transfer in a separate thread."""  
        try:  
            peer_ip = conn.getpeername()[0]
            # Receive public key  
            peer_public_key_bytes = conn.recv(1024)  
            conn.sendall(self.security.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,  # Use PEM encoding
                format=serialization.PublicFormat.SubjectPublicKeyInfo  # Use SubjectPublicKeyInfo format
            ))

            # Generate shared AES key  
            aes_key = self.security.generate_shared_key(peer_public_key_bytes)  

            # Receive encrypted file  
            logging.info(f"Receiving encrypted file from {peer_ip}...") 
            with open("received_file.enc", 'wb') as f:  
                while True:  
                    chunk = conn.recv(4096)  
                    if not chunk:  
                        break  
                    f.write(chunk)  

            # Decrypt file  
            decrypted_file = self.security.decrypt_file("received_file.enc", aes_key)  
            logging.info(f"File received and decrypted from {peer_ip}. Saved as {decrypted_file}.") 
            print(f"File received and decrypted: {decrypted_file}")  
        except Exception as e:  
            print(f"Error handling client: {e}")  
        finally:  
            conn.close()