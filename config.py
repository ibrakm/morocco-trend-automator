#!/usr/bin/env python3
"""
Secure Configuration for Morocco Trend Automator Bot
All tokens are encrypted using Fernet symmetric encryption
"""

from cryptography.fernet import Fernet
import os
import base64

# Generate a key from a secure password (in production, store this securely)
# For now, we'll use environment variable or generate one
def get_encryption_key():
    """Get or create encryption key"""
    key_file = '/home/ubuntu/morocco-bot/.encryption_key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        os.chmod(key_file, 0o600)  # Read/write for owner only
        return key

# Initialize encryption
ENCRYPTION_KEY = get_encryption_key()
cipher = Fernet(ENCRYPTION_KEY)

# Encrypted tokens (encrypted using Fernet symmetric encryption)
ENCRYPTED_TOKENS = {
    'telegram': b'gAAAAABpKWZZfK5ymhOfO1brtTY7an57-ssmk9nWIhY64Lud_t9rGbfFeFuymMWZdR0k-kQcqm2-7A20YOFBQHUxyyHgw0e4mB7zf0DWdoYrr3_ZJqBGPcfBkU4hHTW5ERwx8qOJlHds',
    'perplexity': b'gAAAAABpKNdSV3ex7ZpOanjUkPrIG76y1Pa_SO00uGKGdhPwPx2T7sDx3vuOzZXWAqKAoehhhBnjQ18RGykk-8c7rkb9Ij-IycmUbsPlPmJPEo6oRiNP-HvishjASFyhEewUspNEE0SKrq-JcUsq-6X73nVE7uGrVQ==',
    'gemini': b'gAAAAABpKQc_3NJuyqa6dBpBPvi7XkimgOJ_P_9WMVdWANenNeUMprqP96mcIqApjd4JaySfWjbJQ4ralUrgPrO1mykaR26yswx2wD6xppNbISt03dQeDV8hKRkI0lhBOEh5vb3iO70i',
    'linkedin_token': b'gAAAAABpKNdS0lAdcnREs1mwB9pWDeI6L9gcnU9DN8xLKuNYfuCKXKbfqLO4O4ssw9_qoqaiJtKAsyqY4RtNwLgxBBaf60UB4ai88nCKEDSD7U8X3It7QYfxNUM5_Tvk3XGtlTnv8IVGQguFXz8fDf-RogpHMbDBlVi8bPoII6VietoRMywwFIrRArr4A-OmvALF-km8uSxCThYUbdzVTYaScr1LZUvNLGIbukMzzhORHAZkrcu09cma0dXcmGVDH8RNHWy33mO7Pl6Um_WUGkt90l_UfprbBMLc1JbTJQNgcf-Eu4X8HsLURsmrO4l-nW6KWeY3Frk8RQgdQmwOkPW4otkMnHW6MetJO_F1zZC0hTrxgSKBXWeYlnAbF-D-8M9rgwnZdMuYs6dO2n_sE6EgLsOgUT6CMe9WHyCyV2efyzOeK6CAyen9KWIpC7zMCLwT3MvnUH05PDWs1gz-F1gwosrzAOC-wSw0VC34dy78A2FqKTIsfZSXarjCJYwIYBo54HvaUu6Ot-hCz1ykAz68UmvXw6Qstg==',
    'linkedin_urn': b'gAAAAABpKNdSboamds9kfe5eZIXHPeaVCQZFYV5vEPu-x9MaLWpuy4NrTWpr5zIKxKcy8apD8jnYzm5g9rWzuzA7YVUzblWy-Je5wjkBcHx_MqpfdHxJWrA='
}

def encrypt_token(token: str) -> bytes:
    """Encrypt a token"""
    return cipher.encrypt(token.encode())

def decrypt_token(encrypted_token: bytes) -> str:
    """Decrypt a token"""
    return cipher.decrypt(encrypted_token).decode()

# Function to set up tokens (run once)
def setup_tokens():
    """Encrypt and store all tokens"""
    # SECURITY: Tokens should be provided via environment variables
    # This function is for initial setup only and should not contain hardcoded secrets
    tokens = {
        'telegram': os.getenv('TELEGRAM_BOT_TOKEN', ''),
        'perplexity': os.getenv('PERPLEXITY_API_KEY', ''),
        'gemini': os.getenv('GEMINI_API_KEY', ''),
        'linkedin_token': os.getenv('LINKEDIN_ACCESS_TOKEN', ''),
        'linkedin_urn': os.getenv('LINKEDIN_URN', '')
    }
    
    encrypted = {}
    for key, value in tokens.items():
        encrypted[key] = encrypt_token(value)
        print(f"✅ Encrypted {key}: {encrypted[key][:50]}...")
    
    return encrypted

# Configuration class
class Config:
    """Secure configuration with encrypted tokens"""
    
    @staticmethod
    def get_telegram_token():
        return decrypt_token(ENCRYPTED_TOKENS['telegram'])
    
    @staticmethod
    def get_perplexity_token():
        return decrypt_token(ENCRYPTED_TOKENS['perplexity'])
    
    @staticmethod
    def get_gemini_token():
        return decrypt_token(ENCRYPTED_TOKENS['gemini'])
    
    @staticmethod
    def get_linkedin_token():
        return decrypt_token(ENCRYPTED_TOKENS['linkedin_token'])
    
    @staticmethod
    def get_linkedin_urn():
        return decrypt_token(ENCRYPTED_TOKENS['linkedin_urn'])
    
    # API Endpoints
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_MODEL = "llama-3.1-sonar-small-128k-online"
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    GEMINI_TEXT_MODEL = "gemini-2.0-flash-exp"
    GEMINI_IMAGE_MODEL = "imagen-3.0-generate-001"
    
    LINKEDIN_API_URL = "https://api.linkedin.com/v2"
    
    # Bot Settings
    BOT_USERNAME = "@becool11"
    POLLING_TIMEOUT = 30
    
    # Image Settings
    IMAGE_WIDTH = 1200
    IMAGE_HEIGHT = 630
    LOGO_SIZE = (150, 150)

if __name__ == "__main__":
    # Run this to encrypt tokens for the first time
    print("🔐 Encrypting tokens...")
    encrypted = setup_tokens()
    print("\n✅ All tokens encrypted successfully!")
    print("\n📋 Copy these encrypted values to ENCRYPTED_TOKENS in config.py:")
    for key, value in encrypted.items():
        print(f"    '{key}': {value},")
