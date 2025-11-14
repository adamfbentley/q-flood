from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import generate_api_key, hash_api_key
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/generate-api-key", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(api_key_create: APIKeyCreate, db: Session = Depends(get_db)):
    """Generates a new API key for internal/admin use."""
    raw_key = generate_api_key()
    hashed_key = hash_api_key(raw_key)

    db_api_key = APIKey(
        hashed_key=hashed_key,
        description=api_key_create.description,
        is_active=api_key_create.is_active
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    # Return the raw key only once upon creation
    return APIKeyResponse(
        id=db_api_key.id,
        key=raw_key, # This is the sensitive part, only returned once
        description=db_api_key.description,
        is_active=db_api_key.is_active,
        created_at=db_api_key.created_at
    )
