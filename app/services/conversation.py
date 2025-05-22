"""Conversation service for managing chat conversations."""
import json
import logging
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

from app.config.settings import settings
from app.db.redis_client import RedisClient
from app.models.chat import (
    ConversationThread,
    ConversationThreadRedis,
    StudentMessage,
    TutorMessage,
    ContentResponse
)
from app.services.tutor import tutor_service
from app.services.c3 import c3_service

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation threads."""
    
    def __init__(self):
        """Initialize the conversation service."""
        self.redis_client = RedisClient
        self.tutor_service = tutor_service
        self.c3_service = c3_service
    
    async def create_thread(self, student_id: str, content: ContentResponse) -> ConversationThread:
        """Create a new conversation thread.
        
        Args:
            student_id: ID of the student
            content: Content to discuss in the thread
            
        Returns:
            Created conversation thread
        """
        # Create a new thread
        thread = ConversationThread(
            id=str(uuid.uuid4()),
            student_id=student_id,
            usmos=content.usmos,
            content_id=content.content_id,
            messages=[]
        )
        
        # Save the thread to Redis
        await self._save_thread(thread)
        
        return thread
    
    async def start_conversation(self, student_id: str, usmos: List[str]) -> Dict:
        """Start a conversation based on USMOS.
        
        Args:
            student_id: ID of the student
            usmos: List of USMOS to retrieve content for
            
        Returns:
            Dictionary with conversation threads and content
        """
        try:
            # Get content from C3 service
            contents = await self.c3_service.get_mock_content(usmos)
            if not contents:
                logger.warning(f"No content found for USMOS: {usmos}")
                return {"threads": [], "contents": []}
            
            # Create a thread for each content
            threads = []
            for content in contents:
                thread = await self.create_thread(student_id, content)
                threads.append(thread)
            
            return {
                "threads": threads,
                "contents": contents
            }
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise

    async def get_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get a conversation thread by ID.
        
        Args:
            thread_id: ID of the thread to get
            
        Returns:
            Conversation thread, or None if not found
        """
        try:
            # Get the thread from Redis
            thread_redis = ConversationThreadRedis.get(thread_id)
            if not thread_redis:
                return None
            
            # Convert Redis model to Pydantic model
            messages = json.loads(thread_redis.messages)
            
            # Convert message dictionaries to appropriate types
            typed_messages = []
            for message in messages:
                if message.get("action") is not None:
                    typed_messages.append(StudentMessage(**message))
                else:
                    typed_messages.append(TutorMessage(**message))
            
            # Get content_id from content_ids
            content_ids = json.loads(thread_redis.content_ids)
            content_id = content_ids[0] if content_ids else None
            
            return ConversationThread(
                id=thread_redis.id,
                student_id=thread_redis.student_id,
                usmos=json.loads(thread_redis.usmos_json),
                content_id=content_id,
                messages=typed_messages,
                created_at=datetime.fromisoformat(thread_redis.created_at),
                updated_at=datetime.fromisoformat(thread_redis.updated_at)
            )
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {e}")
            return None
    
    async def add_message(self, message: StudentMessage | TutorMessage) -> ConversationThread:
        """Add a message to a conversation thread.
        
        Args:
            message: Message to add
            
        Returns:
            Updated conversation thread
        """
        # Get the thread
        thread = await self.get_thread(message.conversation_id)
        if not thread:
            raise ValueError(f"Thread {message.conversation_id} not found")
        
        # Add the message
        thread.messages.append(message)
        thread.updated_at = datetime.now(timezone.utc)
        
        # Save the thread
        await self._save_thread(thread)
        
        return thread
    
    async def get_content(self, content_id: str) -> Optional[ContentResponse]:
        """Get content by ID.
        
        Args:
            content_id: ID of the content to get
            
        Returns:
            Content, or None if not found
        """
        try:
            # In a real implementation, this would retrieve the content from the C3 service
            # For now, we'll use a mock implementation
            mock_content = {
                "content123": ContentResponse(
                    content_id="content123",
                    usmos=["MATH.ALG.1"],
                    problem="Solve for x: x + 5 = 10",
                    answer="x = 5",
                    explanation="Subtract 5 from both sides to isolate x."
                ),
                "content456": ContentResponse(
                    content_id="content456",
                    usmos=["MATH.ALG.2"],
                    problem="Solve the system of equations: x + y = 10, x - y = 4",
                    answer="x = 7, y = 3",
                    explanation="Add the equations to eliminate y and solve for x, then substitute to find y."
                ),
                "content789": ContentResponse(
                    content_id="content789",
                    usmos=["SCIENCE.PHYS.1"],
                    problem="A ball is thrown upward with an initial velocity of 20 m/s. How high will it go?",
                    answer="20.4 meters",
                    explanation="Use the formula h = v²/(2g) where g = 9.8 m/s²."
                )
            }
            
            return mock_content.get(content_id)
        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            return None
    
    async def handle_student_action(self, message: StudentMessage) -> TutorMessage:
        """Handle a student action.
        
        Args:
            message: Student message
            
        Returns:
            Tutor's response
        """
        # Get the thread
        thread = await self.get_thread(message.conversation_id)
        if not thread:
            raise ValueError(f"Thread {message.conversation_id} not found")
        
        # Get the content
        content = await self.get_content(thread.content_id)
        if not content:
            raise ValueError(f"Content {thread.content_id} not found")
        
        # Add the message to the thread
        thread = await self.add_message(message)
        
        # Handle the action
        if message.action == "regenerate":
            return await self.regenerate_tutor_response(message.conversation_id)
        else:
            # Generate a response
            response = await self.tutor_service.generate_response(thread, content)
            
            # Add the response to the thread
            await self.add_message(response)
            
            return response
    
    async def regenerate_tutor_response(self, thread_id: str) -> TutorMessage:
        """Regenerate the last tutor response.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            Regenerated tutor message
        """
        # Get the thread
        thread = await self.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
        
        # Get the content
        content = await self.get_content(thread.content_id)
        if not content:
            raise ValueError(f"Content {thread.content_id} not found")
        
        # Remove the last tutor message if it exists
        if thread.messages and isinstance(thread.messages[-1], TutorMessage):
            thread.messages.pop()
            await self._save_thread(thread)
        
        # Generate a new response
        response = await self.tutor_service.generate_response(thread, content)
        
        # Add the response to the thread
        await self.add_message(response)
        
        return response
    
    async def _save_thread(self, thread: ConversationThread) -> None:
        """Save a conversation thread to Redis.
        
        Args:
            thread: Thread to save
        """
        try:
            # Convert messages to dictionaries with datetime serialization
            message_dicts = []
            for message in thread.messages:
                msg_dict = message.model_dump()
                # Convert datetime objects to ISO format strings
                if 'timestamp' in msg_dict and msg_dict['timestamp']:
                    msg_dict['timestamp'] = msg_dict['timestamp'].isoformat()
                message_dicts.append(msg_dict)
            
            # Create Redis model
            thread_redis = ConversationThreadRedis(
                id=thread.id,
                student_id=thread.student_id,
                usmos_json=json.dumps(thread.usmos),
                content_ids=json.dumps([thread.content_id]),  # For now, just one content ID
                messages=json.dumps(message_dicts),
                created_at=thread.created_at.isoformat(),
                updated_at=thread.updated_at.isoformat(),
                is_active=True
            )
            
            # Save to Redis
            thread_redis.save()
        except Exception as e:
            logger.error(f"Error saving thread {thread.id}: {e}")
            raise


# Singleton instance
conversation_service = ConversationService()