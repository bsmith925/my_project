"""Chat API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List

from app.models.chat import (
    UsmosRequest,
    ContentResponse,
    ConversationThread,
    StudentMessage,
    TutorMessage,
    StartConversationResponse
)
from app.services.c3 import c3_service
from app.services.conversation import conversation_service

router = APIRouter()


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(
    request: UsmosRequest,
    student_id: str = Query(..., description="ID of the student")
):
    """Start a new conversation based on USMOS.
    
    Args:
        request: USMOS request
        student_id: ID of the student
        
    Returns:
        Created conversation threads and content
    """
    try:
        # Start conversation with USMOS
        result = await conversation_service.start_conversation(student_id, request.usmos)
        
        return StartConversationResponse(
            threads=result.get("threads", []), 
            contents=result.get("contents", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=TutorMessage)
async def send_message(message: StudentMessage):
    """Send a message to the conversation.
    
    Args:
        message: Student message
        
    Returns:
        Tutor's response
    """
    try:
        # Handle the student action
        response = await conversation_service.handle_student_action(message)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate", response_model=TutorMessage)
async def regenerate_response(request: dict):
    """Regenerate the last tutor response.
    
    Args:
        request: Request with conversation_id
        
    Returns:
        Regenerated tutor message
    """
    try:
        # Validate request
        if "conversation_id" not in request:
            raise HTTPException(status_code=400, detail="conversation_id is required")
        
        # Regenerate the response
        response = await conversation_service.regenerate_tutor_response(request["conversation_id"])
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}", response_model=ConversationThread)
async def get_conversation(conversation_id: str):
    """Get a conversation by ID.
    
    Args:
        conversation_id: ID of the conversation to get
        
    Returns:
        Conversation thread
    """
    try:
        # Get the thread
        thread = await conversation_service.get_thread(conversation_id)
        if not thread:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))