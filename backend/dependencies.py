import logging
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.core.security import verify_api_key
from backend.models.api_key import APIKey

logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    """Dependency to validate API key from request header."""
    # CQ-004: Updated comment regarding scalability for bcrypt-based API key verification.
    # Due to bcrypt's non-deterministic nature, direct database lookup by hashed_key is not possible.
    # This approach iterates through active API keys and verifies them.
    # For very large numbers of API keys, a more scalable authentication mechanism
    # or a system involving a non-secret key identifier for initial lookup might be considered
    # in future iterations.
    stored_api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
    
    for key_obj in stored_api_keys:
        if verify_api_key(api_key, key_obj.hashed_key):
            logger.info(f"API Key '{key_obj.id}' successfully authenticated.")
            return key_obj
    
    logger.warning("Authentication failed: Invalid or inactive API Key provided.")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or inactive API Key",
    )
