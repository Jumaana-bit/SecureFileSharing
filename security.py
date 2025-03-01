from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class Security:
    def __init__(self):
        # Generate ECDH key pair
        self.private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        self.public_key = self.private_key.public_key()

    def generate_shared_key(self, peer_public_key_bytes):
        """Generates a shared AES key using ECDH key exchange"""
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), peer_public_key_bytes)
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)
        return shared_secret[:32]  # Use first 32 bytes as AES key

    def encrypt_file(self, file_path, key):
        """Encrypts a file using AES-256"""
        iv = os.urandom(16)  # Initialization vector
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Ensure data is padded to 16 bytes
        padded_data = file_data + b' ' * (16 - len(file_data) % 16)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_file_path = file_path + ".enc"
        with open(encrypted_file_path, 'wb') as f:
            f.write(iv + encrypted_data)

        return encrypted_file_path

    def decrypt_file(self, encrypted_file_path, key):
        """Decrypts a file using AES-256"""
        with open(encrypted_file_path, 'rb') as f:
            iv = f.read(16)
            encrypted_data = f.read()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        decrypted_file_path = encrypted_file_path.replace(".enc", "_decrypted")
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data.strip())  # Remove padding

        return decrypted_file_path
