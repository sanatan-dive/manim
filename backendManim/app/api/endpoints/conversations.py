from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.core.security import get_current_active_user
from app.services.database_service import db_service
from pydantic import BaseModel
from datetime import datetime
from app.api.endpoints.jobs import JobResponse

router = APIRouter()

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    # jobs: Optional[List[JobResponse]] = None # Optional, usually fetched via get detail

    class Config:
        from_attributes = True

class ConversationDetailResponse(ConversationResponse):
    jobs: List[JobResponse]

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new conversation."""
    return await db_service.create_conversation(user_id=current_user.id, title=conversation.title)

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_active_user)
):
    """List user's conversations."""
    return await db_service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get conversation details with jobs (messages)."""
    conversation = await db_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Ensure jobs is a list, defaulting to empty if None (shouldn't happen with include query)
    conversation['jobs'] = conversation.get('jobs', [])
    return conversation

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    update: ConversationCreate,
    current_user = Depends(get_current_active_user)
):
    """Update conversation title."""
    conversation = await db_service.update_conversation(
        conversation_id=conversation_id,
        title=update.title,
        user_id=current_user.id
    )
    if not conversation:
         raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str, 
    current_user = Depends(get_current_active_user)
):
    """Delete a conversation."""
    result = await db_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "id": conversation_id}
