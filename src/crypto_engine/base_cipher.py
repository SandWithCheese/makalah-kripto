"""
Abstract base class for AEAD cipher implementations
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseCipher(ABC):
    """
    Base interface for Authenticated Encryption with Associated Data (AEAD)
    
    This interface ensures both ASCON and AES implementations follow
    the same contract for encryption/decryption operations.
    """
    
    @abstractmethod
    def encrypt_command(
        self, 
        plaintext: bytes, 
        associated_data: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext with AEAD
        
        Args:
            plaintext: The unlock command or data to encrypt
            associated_data: Additional authenticated data (e.g., Lock ID)
        
        Returns:
            Tuple of (nonce, ciphertext_with_tag)
        """
        pass
    
    @abstractmethod
    def decrypt_command(
        self, 
        nonce: bytes, 
        associated_data: bytes, 
        ciphertext: bytes
    ) -> Optional[bytes]:
        """
        Decrypt and verify ciphertext with AEAD
        
        Args:
            nonce: The nonce used during encryption
            associated_data: Additional authenticated data (must match encryption)
            ciphertext: The ciphertext with authentication tag
        
        Returns:
            Plaintext if authentication succeeds, None otherwise
        """
        pass
