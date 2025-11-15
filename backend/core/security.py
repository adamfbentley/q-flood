import secrets
import hashlib

def hash_api_key(api_key: str) -> str:
    """Hashes an API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verifies a plain API key against its hashed version."""
    return hash_api_key(plain_api_key) == hashed_api_key

def generate_api_key(length: int = 32) -> str:
    """Generates a cryptographically secure random API key."""
    return secrets.token_urlsafe(length)
