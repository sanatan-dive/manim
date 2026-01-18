from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.algorithms import RSAAlgorithm
import json
import httpx
from config import settings
from app.services.database_service import db_service

security = HTTPBearer()

async def get_clerk_public_key(kid: str):
    """Fetch Clerk public key from JWKS"""
    if not settings.CLERK_ISSUER:
        # Development fallback or error
        return None
        
    jwks_url = f"{settings.CLERK_ISSUER}/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        jwks = response.json()
        
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return RSAAlgorithm.from_jwk(json.dumps(key))
    return None

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the JWT token from Clerk"""
    token = credentials.credentials
    
    try:
        # First decode header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header")

        # In production, cache this key!
        public_key = await get_clerk_public_key(kid)
        
        if not public_key:
             # Fallback if no issuer configured (Checking dev mode)
            if not settings.CLERK_ISSUER:
                 # WARNING: Insecure for production, but might be needed if they haven't set env yet
                 # For now, let's enforce it or decode without verification if needed just to get sub
                 # But verify_token implies security.
                 raise HTTPException(status_code=500, detail="CLERK_ISSUER not configured")
            raise HTTPException(status_code=401, detail="Public key not found")

        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE, # Optional verification
            # Clerk tokens might not have audience or it might be the frontend URL
            options={"verify_aud": False} 
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(payload: dict = Depends(verify_token)):
    """
    Get the current user from the database based on Clerk ID.
    If user doesn't exist, create them (Sync).
    """
    clerk_id = payload.get("sub")
    email = payload.get("email") # Clerk usually passes email in jwt if configured, or we need to fetch user
    
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Token missing subject (clerk_id)")

    # Try to find user
    user = await db_service.prisma.user.find_unique(where={"clerkId": clerk_id})
    
    if not user:
        # Create user if email exists in payload or fallback
        # Note: Clerk JWT usually has 'email' if validation is setup
        # If not, we might need to fetch from Clerk API.
        # For this implementation, we assume creating a record is safe.
        
        # If email isn't in token, we might fail or use a placeholder.
        # Clerk default JWT template often doesn't include email unless customized.
        # We'll use a placeholder or try to extract it.
        # Ideally, frontend calls /sync to provide details, but implicit creation is smoother.
        
        user_email = email if email else f"{clerk_id}@clerk.user"
        
        user = await db_service.prisma.user.create(
            data={
                "clerkId": clerk_id,
                "email": user_email,
                "name": payload.get("name", "User"),
            }
        )
        
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user
