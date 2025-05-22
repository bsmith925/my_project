"""Chat conversation models."""
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
import uuid
from redis_om import HashModel, Field as RedisField


class StudentMessage(BaseModel):
    """Student message model."""
    conversation_id: str
    content: str
    action: Literal["question", "answer", "chat", "regenerate"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "conversation_id": "conv123",
                "content": "How do I solve this equation?",
                "action": "question",
                "timestamp": "2025-05-22T12:00:00Z"
            }
        }


class TutorMessage(BaseModel):
    """Tutor message model."""
    conversation_id: str
    content: str
    feedback: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "conversation_id": "conv123",
                "content": "To solve this equation, you need to isolate the variable.",
                "feedback": {"clarity": 0.9, "helpfulness": 0.85},
                "timestamp": "2025-05-22T12:01:00Z"
            }
        }


class ConversationThread(BaseModel):
    """Conversation thread model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    usmos: List[str]
    content_id: str
    messages: List[Any] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "conv123",
                "student_id": "student123",
                "usmos": ["MATH.ALG.1", "MATH.ALG.2"],
                "content_id": "content456",
                "messages": [],
                "created_at": "2025-05-22T12:00:00Z",
                "updated_at": "2025-05-22T12:00:00Z"
            }
        }


class ConversationThreadRedis(HashModel):
    """Redis model for conversation threads."""
    id: str = RedisField(primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id: str = RedisField(index=True)
    usmos_json: str = RedisField(index=True)  # JSON string of usmos
    content_ids: str = RedisField(index=True)  # JSON string of content_ids
    messages: str = RedisField()  # JSON string of messages
    created_at: str = RedisField()  # ISO format string
    updated_at: str = RedisField()  # ISO format string
    is_active: bool = RedisField(default=True, index=True)
    
    class Meta:
        """Redis-OM metadata."""
        model_key_prefix = "conversation_thread"


class UsmosRequest(BaseModel):
    """Request model for USMOS."""
    usmos: List[str]
    
    @field_validator("usmos")
    @classmethod
    def validate_usmos(cls, v):
        """Validate that usmos is not empty."""
        if not v:
            raise ValueError("usmos list cannot be empty")
        return v
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "usmos": ["MATH.ALG.1", "MATH.ALG.2"]
            }
        }


class ContentResponse(BaseModel):
    """Response model for content."""
    content_id: str
    usmos: List[str]
    problem: str
    answer: str
    explanation: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "content_id": "content123",
                "usmos": ["MATH.ALG.1"],
                "problem": "Solve for x: x + 5 = 10",
                "answer": "x = 5",
                "explanation": "Subtract 5 from both sides to isolate x."
            }
        }


class StartConversationResponse(BaseModel):
    """Response model for starting a conversation."""
    threads: List[ConversationThread]
    contents: List[ContentResponse]