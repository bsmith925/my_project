"""Test-driven development approach for chat conversation system."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.models.chat import (
    UsmosRequest,
    ContentResponse,
    ConversationThread,
    StudentMessage,
    TutorMessage,
    StartConversationResponse
)
from app.services.c3 import C3Service
from app.services.tutor import TutorService
from app.services.conversation import ConversationService


class TestChatModels:
    """Test the chat models."""

    def test_student_message_creation(self):
        """Test creating a student message."""
        message = StudentMessage(
            conversation_id="conv123",
            content="How do I solve this equation?",
            action="question"
        )
        
        assert message.conversation_id == "conv123"
        assert message.content == "How do I solve this equation?"
        assert message.action == "question"
        assert isinstance(message.timestamp, datetime)
        
    def test_tutor_message_creation(self):
        """Test creating a tutor message."""
        message = TutorMessage(
            conversation_id="conv123",
            content="To solve this equation, subtract 5 from both sides.",
            feedback={"clarity": 0.9}
        )
        
        assert message.conversation_id == "conv123"
        assert message.content == "To solve this equation, subtract 5 from both sides."
        assert message.feedback == {"clarity": 0.9}
        assert isinstance(message.timestamp, datetime)
        
    def test_conversation_thread_creation(self):
        """Test creating a conversation thread."""
        thread = ConversationThread(
            id="conv123",
            student_id="student123",
            usmos=["MATH.ALG.1"],
            content_id="content456",
            messages=[]
        )
        
        assert thread.id == "conv123"
        assert thread.student_id == "student123"
        assert thread.usmos == ["MATH.ALG.1"]
        assert thread.content_id == "content456"
        assert thread.messages == []
        assert isinstance(thread.created_at, datetime)
        assert isinstance(thread.updated_at, datetime)


class TestC3Service:
    """Test the C3 service."""
    
    @pytest.mark.asyncio
    async def test_get_mock_content(self):
        """Test getting mock content."""
        # Create service
        service = C3Service()
        
        # Get mock content
        content = await service.get_mock_content(["MATH.ALG.1"])
        
        # Assertions
        assert len(content) == 1
        assert content[0].content_id == "content123"
        assert content[0].usmos == ["MATH.ALG.1"]
        assert "Solve for x" in content[0].problem
        assert content[0].answer == "x = 5"


class TestTutorService:
    """Test the tutor service."""
    
    @pytest.mark.asyncio
    async def test_generate_response(self):
        """Test generating a response."""
        # Create service
        service = TutorService()
        
        # Create thread and content
        thread = ConversationThread(
            id="conv123",
            student_id="student123",
            usmos=["MATH.ALG.1"],
            content_id="content123",
            messages=[
                StudentMessage(
                    conversation_id="conv123",
                    content="How do I solve x + 5 = 10?",
                    action="question"
                )
            ]
        )
        
        content = ContentResponse(
            content_id="content123",
            usmos=["MATH.ALG.1"],
            problem="Solve for x: x + 5 = 10",
            answer="x = 5",
            explanation="Subtract 5 from both sides to isolate x."
        )
        
        # Generate response
        response = await service.generate_response(thread, content)
        
        # Assertions
        assert response.conversation_id == "conv123"
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert isinstance(response.feedback, dict)
        assert "clarity" in response.feedback


class TestConversationService:
    """Test the conversation service."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        with patch("app.services.conversation.RedisClient") as mock:
            yield mock
    
    @pytest.fixture
    def mock_c3_service(self):
        """Mock C3 service."""
        with patch("app.services.conversation.c3_service") as mock:
            # Create an awaitable mock for get_mock_content
            async def mock_get_content(usmos):
                return [
                    ContentResponse(
                        content_id="content123",
                        usmos=["MATH.ALG.1"],
                        problem="Solve for x: x + 5 = 10",
                        answer="x = 5",
                        explanation="Subtract 5 from both sides to isolate x."
                    )
                ]
            mock.get_mock_content = mock_get_content
            yield mock
    
    @pytest.fixture
    def mock_tutor_service(self):
        """Mock tutor service."""
        with patch("app.services.conversation.tutor_service") as mock:
            # Create an awaitable mock for generate_response
            async def mock_generate_response(thread, content):
                return TutorMessage(
                    conversation_id="conv123",
                    content="To solve this equation, subtract 5 from both sides.",
                    feedback={"clarity": 0.9}
                )
            mock.generate_response = mock_generate_response
            yield mock
    
    @pytest.fixture
    def mock_conversation_thread_redis(self):
        """Mock ConversationThreadRedis."""
        with patch("app.services.conversation.ConversationThreadRedis") as mock:
            # Mock save method
            mock.return_value.save.return_value = None
            
            # Mock get method
            thread_redis = MagicMock()
            thread_redis.id = "conv123"
            thread_redis.student_id = "student123"
            thread_redis.usmos_json = '["MATH.ALG.1"]'
            thread_redis.content_ids = '["content123"]'
            thread_redis.messages = '[{"conversation_id": "conv123", "content": "How do I solve x + 5 = 10?", "action": "question", "timestamp": "2025-05-22T12:00:00Z"}]'
            thread_redis.created_at = "2025-05-22T12:00:00Z"
            thread_redis.updated_at = "2025-05-22T12:00:00Z"
            mock.get.return_value = thread_redis
            
            yield mock
    
    @pytest.mark.asyncio
    async def test_start_conversation(self, mock_redis_client, mock_c3_service, mock_tutor_service, mock_conversation_thread_redis):
        """Test starting a conversation."""
        # Create service
        service = ConversationService()
        
        # Mock create_thread method
        thread = ConversationThread(
            id="conv123",
            student_id="student123",
            usmos=["MATH.ALG.1"],
            content_id="content123",
            messages=[]
        )
        
        async def mock_create_thread(student_id, content):
            return thread
        service.create_thread = mock_create_thread
        
        # Start conversation
        result = await service.start_conversation("student123", ["MATH.ALG.1"])
        
        # Assertions
        assert "threads" in result
        assert "contents" in result
        assert len(result["threads"]) == 1
        assert len(result["contents"]) == 1
        assert result["threads"][0].student_id == "student123"
        assert result["threads"][0].usmos == ["MATH.ALG.1"]
        assert result["contents"][0].content_id == "content123"
    
    @pytest.mark.asyncio
    async def test_get_thread(self, mock_redis_client, mock_c3_service, mock_tutor_service, mock_conversation_thread_redis):
        """Test getting a thread."""
        # Create service
        service = ConversationService()
        
        # Get thread
        thread = await service.get_thread("conv123")
        
        # Assertions
        assert thread is not None
        assert thread.id == "conv123"
        assert thread.student_id == "student123"
        assert thread.usmos == ["MATH.ALG.1"]
        assert thread.content_id == "content123"
        assert len(thread.messages) == 1
        assert thread.messages[0].conversation_id == "conv123"
        assert thread.messages[0].content == "How do I solve x + 5 = 10?"
    
    @pytest.mark.asyncio
    async def test_handle_student_action(self, mock_redis_client, mock_c3_service, mock_tutor_service, mock_conversation_thread_redis):
        """Test handling a student action."""
        # Create service
        service = ConversationService()
        
        # Mock the get_thread method
        thread = ConversationThread(
            id="conv123",
            student_id="student123",
            usmos=["MATH.ALG.1"],
            content_id="content123",
            messages=[
                StudentMessage(
                    conversation_id="conv123",
                    content="How do I solve x + 5 = 10?",
                    action="question"
                )
            ]
        )
        
        async def mock_get_thread(thread_id):
            return thread
        service.get_thread = mock_get_thread
        
        # Mock the get_content method
        async def mock_get_content(content_id):
            return ContentResponse(
                content_id="content123",
                usmos=["MATH.ALG.1"],
                problem="Solve for x: x + 5 = 10",
                answer="x = 5",
                explanation="Subtract 5 from both sides to isolate x."
            )
        service.get_content = mock_get_content
        
        # Mock the add_message method
        async def mock_add_message(message):
            return thread
        service.add_message = mock_add_message
        
        # Create message
        message = StudentMessage(
            conversation_id="conv123",
            content="How do I solve this equation?",
            action="question"
        )
        
        # Handle action
        response = await service.handle_student_action(message)
        
        # Assertions
        assert response.conversation_id == "conv123"
        assert response.content == "To solve this equation, subtract 5 from both sides."
        assert response.feedback == {"clarity": 0.9}