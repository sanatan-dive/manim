import jwt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_active_user
from app.services.database_service import db_service
from pydantic import BaseModel
import secrets
import string

router = APIRouter()

class UserResponse(BaseModel):
    id: str
    clerkId: str | None
    email: str
    name: str | None
    apiKey: str | None
    credits: int
    generationCount: int
    plan: str
    
    class Config:
        from_attributes = True

class APIKeyResponse(BaseModel):
    apiKey: str

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Get current user profile.
    """
    return current_user

@router.post("/sync", response_model=UserResponse)
async def sync_user(
    current_user = Depends(get_current_active_user)
):
    """
    Explicit sync endpoint to ensure user exists and return data.
    """
    return current_user

@router.post("/api-key", response_model=APIKeyResponse)
async def generate_api_key(current_user = Depends(get_current_active_user)):
    """
    Generate or rotate API Key for the user.
    """
    # Generate a secure random API key
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for i in range(32))
    
    # Update user in DB
    updated_user = await db_service.prisma.user.update(
        where={"id": current_user.id},
        data={"apiKey": api_key}
    )
    
    return {"apiKey": updated_user.apiKey}

@router.get("/usage")
async def get_usage(current_user = Depends(get_current_active_user)):
    """
    Get usage statistics.
    """
    return {
        "credits": current_user.credits,
        "generation_count": current_user.generationCount,
        "plan": current_user.plan
    }
