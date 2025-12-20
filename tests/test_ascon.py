"""
Unit tests for ASCON-128 wrapper

Tests encryption/decryption correctness, nonce uniqueness, 
and authentication failure detection.
"""
import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto_engine import AsconLock


class TestAsconLock:
    """Test suite for ASCON-128 implementation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.cipher = AsconLock()
        self.plaintext = b"unlock_bike_id_12345"
        self.associated_data = b"lock_station_A_slot_42"
    
    def test_encryption_produces_output(self):
        """Test that encryption produces non-empty ciphertext"""
        nonce, ciphertext = self.cipher.encrypt_command(
            self.plaintext, 
            self.associated_data
        )
        
        assert nonce is not None
        assert len(nonce) == 16  # 128-bit nonce
        assert ciphertext is not None
        assert len(ciphertext) > len(self.plaintext)  # Includes tag
    
    def test_decryption_roundtrip(self):
        """Test encrypt -> decrypt returns original plaintext"""
        nonce, ciphertext = self.cipher.encrypt_command(
            self.plaintext,
            self.associated_data
        )
        
        decrypted = self.cipher.decrypt_command(
            nonce,
            self.associated_data,
            ciphertext
        )
        
        assert decrypted == self.plaintext
    
    def test_nonce_uniqueness(self):
        """Test that nonces are unique across multiple encryptions"""
        nonces = set()
        
        for _ in range(100):
            nonce, _ = self.cipher.encrypt_command(
                self.plaintext,
                self.associated_data
            )
            nonces.add(nonce)
        
        assert len(nonces) == 100  # All unique
    
    def test_authentication_failure_tampered_ciphertext(self):
        """Test that tampered ciphertext fails authentication"""
        nonce, ciphertext = self.cipher.encrypt_command(
            self.plaintext,
            self.associated_data
        )
        
        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0x01  # Flip one bit
        tampered = bytes(tampered)
        
        # Should return None (authentication failure)
        result = self.cipher.decrypt_command(
            nonce,
            self.associated_data,
            tampered
        )
        
        assert result is None
    
    def test_authentication_failure_wrong_associated_data(self):
        """Test that wrong associated data fails authentication"""
        nonce, ciphertext = self.cipher.encrypt_command(
            self.plaintext,
            self.associated_data
        )
        
        # Use different associated data
        wrong_ad = b"different_lock_id"
        
        result = self.cipher.decrypt_command(
            nonce,
            wrong_ad,
            ciphertext
        )
        
        assert result is None
    
    def test_authentication_failure_wrong_nonce(self):
        """Test that wrong nonce fails decryption"""
        _, ciphertext = self.cipher.encrypt_command(
            self.plaintext,
            self.associated_data
        )
        
        # Use different nonce
        wrong_nonce = os.urandom(16)
        
        result = self.cipher.decrypt_command(
            wrong_nonce,
            self.associated_data,
            ciphertext
        )
        
        assert result is None
    
    def test_different_plaintexts_different_ciphertexts(self):
        """Test that different inputs produce different outputs"""
        nonce1, ct1 = self.cipher.encrypt_command(
            b"plaintext1",
            self.associated_data
        )
        
        nonce2, ct2 = self.cipher.encrypt_command(
            b"plaintext2",
            self.associated_data
        )
        
        assert ct1 != ct2
        assert nonce1 != nonce2  # Nonces should be different too
    
    def test_empty_plaintext(self):
        """Test encryption of empty plaintext"""
        nonce, ciphertext = self.cipher.encrypt_command(
            b"",
            self.associated_data
        )
        
        decrypted = self.cipher.decrypt_command(
            nonce,
            self.associated_data,
            ciphertext
        )
        
        assert decrypted == b""
    
    def test_large_plaintext(self):
        """Test encryption of larger plaintext (1KB)"""
        large_plaintext = b"X" * 1024
        
        nonce, ciphertext = self.cipher.encrypt_command(
            large_plaintext,
            self.associated_data
        )
        
        decrypted = self.cipher.decrypt_command(
            nonce,
            self.associated_data,
            ciphertext
        )
        
        assert decrypted == large_plaintext
    
    def test_key_initialization_with_custom_key(self):
        """Test initialization with custom key"""
        custom_key = os.urandom(16)
        cipher = AsconLock(key=custom_key)
        
        assert cipher.key == custom_key
    
    def test_key_initialization_invalid_size(self):
        """Test that invalid key size raises error"""
        with pytest.raises(ValueError):
            AsconLock(key=b"short")  # Too short
    
    def test_algorithm_name(self):
        """Test algorithm name method"""
        assert self.cipher.get_algorithm_name() == "ASCON-128"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
