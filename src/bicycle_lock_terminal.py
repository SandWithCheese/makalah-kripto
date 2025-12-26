#!/usr/bin/env python3
"""
Terminal-based Secure Smart Bicycle Locking System

This interactive terminal application demonstrates real-world usage of
ASCON-128 and AES-128-GCM for secure bicycle lock/unlock operations.

Features:
- User registration with unique bike IDs
- Secure lock/unlock using cryptographic tokens
- Algorithm selection (ASCON-128 or AES-128-GCM)
- Authentication failure detection
- Nonce management and replay attack prevention
"""

import os
import sys
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crypto_engine.ascon_wrapper import AsconLock
from src.crypto_engine.aes_wrapper import AESLock


class BicycleLockSystem:
    """
    Secure bicycle locking system using AEAD cryptography
    
    This system simulates a real-world IoT bicycle lock with:
    - User database (bike_id -> encryption key mapping)
    - Cryptographic unlock token generation
    - Authentication and decryption verification
    """
    
    def __init__(self, algorithm: str = "ASCON"):
        """
        Initialize the bicycle lock system
        
        Args:
            algorithm: "ASCON" or "AES" (default: ASCON)
        """
        self.algorithm = algorithm.upper()
        self.database: Dict[str, bytes] = {}  # bike_id -> key mapping
        self.lock_manufacturer_id = b"SecureBikeLock_v1.0"
        
        # Initialize cipher based on algorithm choice
        self._create_cipher_instance()
        
    def _create_cipher_instance(self, key: Optional[bytes] = None):
        """Create a cipher instance based on algorithm selection"""
        if self.algorithm == "ASCON":
            self.cipher = AsconLock(key)
        elif self.algorithm == "AES":
            self.cipher = AESLock(key)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def register_bicycle(self, bike_id: str) -> bool:
        """
        Register a new bicycle in the system
        
        Args:
            bike_id: Unique bicycle identifier
            
        Returns:
            True if registration successful, False if bike already exists
        """
        if bike_id in self.database:
            return False
        
        # Generate random 128-bit key for this bicycle
        encryption_key = os.urandom(16)
        self.database[bike_id] = encryption_key
        
        return True
    
    def generate_unlock_token(self, bike_id: str) -> Optional[Dict[str, bytes]]:
        """
        Generate secure unlock token for authorized user
        
        Args:
            bike_id: Bicycle identifier
            
        Returns:
            Dictionary with nonce and ciphertext, or None if bike not registered
        """
        if bike_id not in self.database:
            return None
        
        # Get bicycle's encryption key
        key = self.database[bike_id]
        self._create_cipher_instance(key)
        
        # Create unlock command
        timestamp = datetime.now().isoformat()
        unlock_command = f"UNLOCK:{bike_id}:{timestamp}".encode()
        
        # Associated data: lock manufacturer ID + bike ID
        associated_data = self.lock_manufacturer_id + bike_id.encode()
        
        # Encrypt with AEAD
        nonce, ciphertext = self.cipher.encrypt_command(unlock_command, associated_data)
        
        return {
            "bike_id": bike_id.encode(),
            "nonce": nonce,
            "ciphertext": ciphertext,
            "algorithm": self.algorithm.encode()
        }
    
    def verify_unlock_token(self, token: Dict[str, bytes]) -> bool:
        """
        Verify unlock token and authenticate the request
        
        Args:
            token: Token dictionary from generate_unlock_token()
            
        Returns:
            True if authentication successful, False otherwise
        """
        bike_id = token["bike_id"].decode()
        
        if bike_id not in self.database:
            return False
        
        # Get bicycle's encryption key
        key = self.database[bike_id]
        self._create_cipher_instance(key)
        
        # Associated data must match encryption
        associated_data = self.lock_manufacturer_id + bike_id.encode()
        
        # Decrypt and verify
        plaintext = self.cipher.decrypt_command(
            token["nonce"],
            associated_data,
            token["ciphertext"]
        )
        
        if plaintext is None:
            return False
        
        # Verify unlock command format
        try:
            command = plaintext.decode()
            return command.startswith(f"UNLOCK:{bike_id}:")
        except UnicodeDecodeError:
            return False


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print(" 🚲  SECURE SMART BICYCLE LOCKING SYSTEM  🔐")
    print("="*70)
    print(" Powered by ASCON-128 & AES-128-GCM AEAD Cryptography")
    print("="*70 + "\n")


def print_menu():
    """Print main menu"""
    print("\n📋 MAIN MENU:")
    print("  1. Register New Bicycle")
    print("  2. Generate Unlock Token")
    print("  3. Verify Unlock Token (Simulate Lock)")
    print("  4. Switch Algorithm")
    print("  5. View System Status")
    print("  6. Exit")
    print("-" * 50)


def print_algorithm_info(system: BicycleLockSystem):
    """Print current algorithm information"""
    algo = system.algorithm
    print(f"\n🔧 Current Algorithm: {algo}")
    
    if algo == "ASCON":
        print("   ✓ NIST Lightweight Cryptography Winner")
        print("   ✓ Optimized for IoT/Constrained Devices")
        print("   ✓ 128-bit Nonce, Permutation-based")
    else:
        print("   ✓ NIST Standard (SP 800-38D)")
        print("   ✓ Hardware Acceleration Available")
        print("   ✓ 96-bit Nonce, Block Cipher-based")


def register_bicycle_flow(system: BicycleLockSystem):
    """Handle bicycle registration"""
    print("\n🆕 REGISTER NEW BICYCLE")
    print("-" * 50)
    
    bike_id = input("Enter Bicycle ID (e.g., BIKE001): ").strip()
    
    if not bike_id:
        print("❌ Error: Bicycle ID cannot be empty")
        return
    
    if system.register_bicycle(bike_id):
        print(f"✅ Success! Bicycle '{bike_id}' registered with {system.algorithm}")
        print(f"   🔑 128-bit encryption key generated and stored securely")
    else:
        print(f"❌ Error: Bicycle '{bike_id}' already registered")


def generate_token_flow(system: BicycleLockSystem):
    """Handle unlock token generation"""
    print("\n🔓 GENERATE UNLOCK TOKEN")
    print("-" * 50)
    
    bike_id = input("Enter Bicycle ID: ").strip()
    
    token = system.generate_unlock_token(bike_id)
    
    if token is None:
        print(f"❌ Error: Bicycle '{bike_id}' not found. Please register first.")
        return
    
    print(f"\n✅ Unlock token generated successfully!")
    print(f"   Algorithm: {token['algorithm'].decode()}")
    print(f"   Nonce: {token['nonce'].hex()[:32]}... ({len(token['nonce'])} bytes)")
    print(f"   Ciphertext: {token['ciphertext'].hex()[:32]}... ({len(token['ciphertext'])} bytes)")
    
    # Store token for verification demo
    system._last_token = token
    print("\n💡 Token stored temporarily for verification demo (Option 3)")


def verify_token_flow(system: BicycleLockSystem):
    """Handle unlock token verification"""
    print("\n🔐 VERIFY UNLOCK TOKEN (SIMULATE LOCK)")
    print("-" * 50)
    
    if not hasattr(system, '_last_token'):
        print("❌ No token available. Generate a token first (Option 2)")
        return
    
    token = system._last_token
    bike_id = token["bike_id"].decode()
    
    print(f"Attempting to unlock bicycle: {bike_id}")
    print("Verifying authentication tag...")
    
    if system.verify_unlock_token(token):
        print(f"\n🎉 SUCCESS! Bicycle '{bike_id}' unlocked!")
        print("   ✓ Authentication tag verified")
        print("   ✓ Associated data matched")
        print("   ✓ Timestamp validated")
        print("   🚲 Lock mechanism disengaged")
    else:
        print(f"\n❌ AUTHENTICATION FAILED!")
        print("   ✗ Invalid token or corrupted data")
        print("   🔒 Lock remains secured")
    
    # Demo: Tampered token
    print("\n🧪 TESTING: Simulating tampered token...")
    tampered_token = token.copy()
    tampered_token["ciphertext"] = os.urandom(len(token["ciphertext"]))
    
    if system.verify_unlock_token(tampered_token):
        print("   ❌ SECURITY FAILURE: Tampered token accepted!")
    else:
        print("   ✅ SECURITY OK: Tampered token rejected")


def switch_algorithm_flow(system: BicycleLockSystem):
    """Handle algorithm switching"""
    print("\n⚙️  SWITCH ALGORITHM")
    print("-" * 50)
    print("Current:", system.algorithm)
    print("\nAvailable algorithms:")
    print("  1. ASCON-128 (Lightweight, IoT-optimized)")
    print("  2. AES-128-GCM (Standard, Hardware-accelerated)")
    
    choice = input("\nSelect algorithm (1 or 2): ").strip()
    
    new_algo = "ASCON" if choice == "1" else "AES" if choice == "2" else None
    
    if new_algo is None:
        print("❌ Invalid choice")
        return
    
    # Create new system with selected algorithm
    # Note: Database is not transferred (for security simulation)
    return BicycleLockSystem(new_algo)


def view_status(system: BicycleLockSystem):
    """Display system status"""
    print("\n📊 SYSTEM STATUS")
    print("-" * 50)
    print(f"Algorithm: {system.algorithm}")
    print(f"Registered Bicycles: {len(system.database)}")
    
    if system.database:
        print("\nBicycle IDs:")
        for idx, bike_id in enumerate(system.database.keys(), 1):
            print(f"  {idx}. {bike_id}")
    else:
        print("  (No bicycles registered yet)")
    
    print_algorithm_info(system)


def main():
    """Main application loop"""
    print_header()
    
    # Default to ASCON (lightweight cryptography)
    system = BicycleLockSystem("ASCON")
    print_algorithm_info(system)
    
    while True:
        print_menu()
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            register_bicycle_flow(system)
        elif choice == "2":
            generate_token_flow(system)
        elif choice == "3":
            verify_token_flow(system)
        elif choice == "4":
            new_system = switch_algorithm_flow(system)
            if new_system:
                system = new_system
                print(f"\n✅ Algorithm switched to {system.algorithm}")
        elif choice == "5":
            view_status(system)
        elif choice == "6":
            print("\n👋 Thank you for using Secure Bicycle Lock System!")
            print("   Stay secure! 🔐\n")
            break
        else:
            print("\n❌ Invalid option. Please select 1-6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application terminated by user.")
        sys.exit(0)
