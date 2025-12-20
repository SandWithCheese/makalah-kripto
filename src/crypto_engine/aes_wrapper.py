"""
AES-128-GCM AEAD wrapper for bicycle lock simulation

AES-GCM is a widely-used authenticated encryption mode standardized by NIST.
It combines AES encryption with Galois/Counter Mode for authentication.

Security Properties:
- 128-bit security level
- Hardware acceleration available on most platforms
- NIST SP 800-38D standard
- Associated data support
"""
import os
from Crypto.Cipher import AES
from typing import Tuple, Optional
from .base_cipher import BaseCipher


class AESLock(BaseCipher):
    """
    AES-128-GCM implementation for secure bicycle lock commands
    
    This wrapper provides AEAD operations using AES in GCM mode,
    ensuring both confidentiality and authenticity of unlock commands.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize AES-GCM lock with encryption key
        
        Args:
            key: 128-bit (16 bytes) secret key. If None, generates random key.
        """
        if key is None:
            self.key = os.urandom(16)  # 128-bit random key
        else:
            if len(key) != 16:
                raise ValueError("AES-128 requires 16-byte (128-bit) key")
            self.key = key
    
    def encrypt_command(
        self, 
        plaintext: bytes, 
        associated_data: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt unlock command with AES-128-GCM
        
        Args:
            plaintext: The unlock command (e.g., b"unlock_bike_id_12345")
            associated_data: Lock ID or additional context
        
        Returns:
            Tuple of (nonce, ciphertext_with_tag)
        
        Note:
            GCM uses 96-bit (12 byte) nonces as per NIST recommendation
        """
        # Generate unique 96-bit nonce (GCM standard)
        nonce = os.urandom(12)
        
        # Create AES-GCM cipher instance
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        
        # Add associated data for authentication
        cipher.update(associated_data)
        
        # Encrypt and generate authentication tag
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # Concatenate ciphertext and tag for unified output
        return nonce, ciphertext + tag
    
    def decrypt_command(
        self, 
        nonce: bytes, 
        associated_data: bytes, 
        ciphertext_tag: bytes
    ) -> Optional[bytes]:
        """
        Decrypt and verify unlock command with AES-128-GCM
        
        Args:
            nonce: The nonce used during encryption
            associated_data: Lock ID (must match encryption)
            ciphertext_tag: Ciphertext concatenated with 16-byte tag
        
        Returns:
            Plaintext if authentication succeeds, None if tag verification fails
        
        Security:
            Returns None on authentication failure, preventing timing attacks
        """
        try:
            # Create AES-GCM cipher instance with same nonce
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            
            # Add associated data for authentication
            cipher.update(associated_data)
            
            # Separate ciphertext and tag (tag is last 16 bytes)
            ciphertext = ciphertext_tag[:-16]
            tag = ciphertext_tag[-16:]
            
            # Decrypt and verify tag in one operation
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return plaintext
        except ValueError:
            # Authentication failed - tag mismatch or corrupted data
            # ValueError is raised by decrypt_and_verify on tag mismatch
            return None
    
    def get_algorithm_name(self) -> str:
        """Return algorithm identifier for benchmarking"""
        return "AES-128-GCM"
