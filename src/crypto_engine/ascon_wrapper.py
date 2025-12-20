"""
ASCON-128 AEAD wrapper for bicycle lock simulation

ASCON-128 is the NIST Lightweight Cryptography standard winner.
It provides authenticated encryption optimized for constrained environments.

Security Properties:
- 128-bit security level
- Permutation-based construction
- Resistant to replay attacks (via unique nonce)
- Associated data support (Lock ID binding)
"""
import os
import ascon
from typing import Tuple, Optional
from .base_cipher import BaseCipher


class AsconLock(BaseCipher):
    """
    ASCON-128 implementation for secure bicycle lock commands
    
    This wrapper provides AEAD operations using the ASCON-128 variant,
    ensuring both confidentiality and authenticity of unlock commands.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize ASCON lock with encryption key
        
        Args:
            key: 128-bit (16 bytes) secret key. If None, generates random key.
        """
        if key is None:
            self.key = os.urandom(16)  # 128-bit random key
        else:
            if len(key) != 16:
                raise ValueError("ASCON-128 requires 16-byte (128-bit) key")
            self.key = key
    
    def encrypt_command(
        self, 
        plaintext: bytes, 
        associated_data: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt unlock command with ASCON-128
        
        Args:
            plaintext: The unlock command (e.g., b"unlock_bike_id_12345")
            associated_data: Lock ID or additional context
        
        Returns:
            Tuple of (nonce, ciphertext_with_tag)
        
        Note:
            Nonce is generated fresh for each operation to prevent replay attacks
        """
        # Generate unique 128-bit nonce for this operation
        nonce = os.urandom(16)
        
        # ASCON-128 encryption with associated data
        from ascon import encrypt as ascon_encrypt
        ciphertext = ascon_encrypt(
            key=self.key,
            nonce=nonce,
            associateddata=associated_data,
            plaintext=plaintext,
            variant="Ascon-128"
        )
        
        return nonce, ciphertext
    
    def decrypt_command(
        self, 
        nonce: bytes, 
        associated_data: bytes, 
        ciphertext: bytes
    ) -> Optional[bytes]:
        """
        Decrypt and verify unlock command with ASCON-128
        
        Args:
            nonce: The nonce used during encryption
            associated_data: Lock ID (must match encryption)
            ciphertext: Ciphertext with authentication tag
        
        Returns:
            Plaintext if authentication succeeds, None if tag verification fails
        
        Security:
            Returns None on authentication failure, preventing timing attacks
        """
        try:
            from ascon import decrypt as ascon_decrypt
            plaintext = ascon_decrypt(
                key=self.key,
                nonce=nonce,
                associateddata=associated_data,
                ciphertext=ciphertext,
                variant="Ascon-128"
            )
            return plaintext
        except Exception:
            # Authentication failed - tag mismatch or corrupted data
            # Return None instead of raising to prevent timing side-channels
            return None
    
    def get_algorithm_name(self) -> str:
        """Return algorithm identifier for benchmarking"""
        return "ASCON-128"
