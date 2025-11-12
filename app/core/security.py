from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_api_key(api_key: str) -> str:
    """Hashes an API key using bcrypt."""
    return pwd_context.hash(api_key)

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verifies a plain API key against its hashed version."""
    return pwd_context.verify(plain_api_key, hashed_api_key)

def generate_api_key(length: int = 32) -> str:
    """Generates a cryptographically secure random API key."""
    return secrets.token_urlsafe(length)
