"""Tests for chat conversation services."""
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from app.models.chat import (
    UsmosRequest,
    ContentResponse,
    ConversationThread,
    StudentMessage,
    TutorMessage
)
from app.services.c3 import C3Service
from app.services.tutor import TutorService
from app.services.conversation import ConversationService

# Remove any import of dspy if it exists


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("redis.Redis") as mock:
        yield mock


@pytest.fixture
def c3_service():
    """Create a C3Service instance with mocked dependencies."""
    service = C3Service()
    service.base_url = "http://c3-api.example.com"
    return service


@pytest.fixture
def tutor_service():
    """Create a TutorService instance."""
    return TutorService()


@pytest.fixture
def conversation_service(mock_redis):
    """Create a ConversationService instance with mocked dependencies."""
    return ConversationService()


@pytest.mark.asyncio
async def test_c3_service_get_content(c3_service):
    """Test C3Service.get_content method."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock the response from C3 service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "content_id": "content123",
                "usmos": ["MATH.ALG.1"],
                "problem": "Solve for x: x + 5 = 10",
                "answer": "x = 5",
                "explanation": "Subtract 5 from both sides to isolate x."
            }
        ]
        mock_get.return_value = mock_response
        
        # Test the method
        usmos_request = UsmosRequest(usmos=["MATH.ALG.1"])
        result = await c3_service.get_content(usmos_request)
        
        # Assertions
        assert len(result) == 1
        assert isinstance(result[0], ContentResponse)
        assert result[0].content_id == "content123"
        assert result[0].problem == "Solve for x: x + 5 = 10"


@pytest.mark.asyncio
async def test_tutor_service_generate_response(tutor_service):
    """Test TutorService.generate_response method."""
    # No need to mock Program since we're not using DSPy directly anymore
    
    # Test data
    thread = ConversationThread(
        id="conv123",
        student_id="student123",
        usmos=["MATH.ALG.1"],
        content_id="content456",
        messages=[
            StudentMessage(
                conversation_id="conv123",
                content="How do I solve x + 5 = 10?",
                action="question"
            )
        ]
    )
    content = ContentResponse(
        content_id="content456",
        usmos=["MATH.ALG.1"],
        problem="Solve for x: x + 5 = 10",
        answer="x = 5",
        explanation="Subtract 5 from both sides to isolate x."
    )
    
    # Test the method
    result = await tutor_service.generate_response(thread, content)
    
    # Assertions
    assert isinstance(result, TutorMessage)
    assert result.conversation_id == "conv123"
    assert "question" in result.content.lower() or "answer" in result.content.lower()


@pytest.mark.asyncio
async def test_conversation_service_create_thread(conversation_service, mock_redis):
    """Test ConversationService.create_thread method."""
    # Mock data
    student_id = "student123"
    content = ContentResponse(
        content_id="content123",
        usmos=["MATH.ALG.1"],
        problem="Solve for x: x + 5 = 10",
        answer="x = 5",
        explanation="Subtract 5 from both sides to isolate x."
    )
    
    # Mock Redis save method
    with patch("app.services.conversation.ConversationThreadRedis.save") as mock_save:
        mock_save.return_value = "thread123"
        
        # Test the method
        thread = await conversation_service.create_thread(student_id, content)
        
        # Assertions
        assert isinstance(thread, ConversationThread)
        assert thread.student_id == "student123"
        assert thread.content_id == "content123"
        assert thread.usmos == ["MATH.ALG.1"]
        assert len(thread.messages) == 0


@pytest.mark.asyncio
async def test_conversation_service_add_message(conversation_service, mock_redis):
    """Test ConversationService.add_message method."""
    # Mock data
    thread = ConversationThread(
        id="conv123",
        student_id="student123",
        usmos=["MATH.ALG.1"],
        content_id="content456",
        messages=[]
    )
    
    message = StudentMessage(
        conversation_id="conv123",
        content="How do I solve this equation?",
        action="question"
    )
    
    # Mock the get_thread method and save method
    with patch.object(conversation_service, "get_thread", return_value=thread), \
         patch("app.services.conversation.ConversationThreadRedis.save"):
        
        # Test the method
        updated_thread = await conversation_service.add_message(message)
        
        # Assertions
        assert len(updated_thread.messages) == 1
        assert updated_thread.messages[0].content == "How do I solve this equation?"
        assert updated_thread.messages[0].action == "question"


@pytest.mark.asyncio
async def test_conversation_service_start_conversation(conversation_service):
    """Test ConversationService.start_conversation method."""
    # Mock data
    student_id = "student123"
    usmos = ["MATH.ALG.1", "MATH.ALG.2"]
    
    # Mock content responses
    mock_contents = [
        ContentResponse(
            content_id="content123",
            usmos=["MATH.ALG.1"],
            problem="Solve for x: x + 5 = 10",
            answer="x = 5",
            explanation="Subtract 5 from both sides to isolate x."
        ),
        ContentResponse(
            content_id="content456",
            usmos=["MATH.ALG.2"],
            problem="Solve the system of equations: x + y = 10, x - y = 4",
            answer="x = 7, y = 3",
            explanation="Add the equations to eliminate y and solve for x, then substitute to find y."
        )
    ]
    
    # Mock methods
    with patch.object(conversation_service.c3_service, "get_mock_content", return_value=mock_contents), \
         patch.object(conversation_service, "create_thread") as mock_create_thread:
        
        # Mock create_thread to return a thread for each content
        mock_create_thread.side_effect = [
            ConversationThread(
                id="thread1",
                student_id=student_id,
                usmos=["MATH.ALG.1"],
                content_id="content123",
                messages=[]
            ),
            ConversationThread(
                id="thread2",
                student_id=student_id,
                usmos=["MATH.ALG.2"],
                content_id="content456",
                messages=[]
            )
        ]
        
        # Test the method
        result = await conversation_service.start_conversation(student_id, usmos)
        
        # Assertions
        assert "threads" in result
        assert "contents" in result
        assert len(result["threads"]) == 2
        assert len(result["contents"]) == 2
        assert result["threads"][0].id == "thread1"
        assert result["threads"][1].id == "thread2"
        assert result["contents"][0].content_id == "content123"
        assert result["contents"][1].content_id == "content456"


@pytest.mark.asyncio
async def test_conversation_service_handle_student_action(conversation_service, tutor_service):
    """Test ConversationService.handle_student_action method."""
    # Mock data
    thread = ConversationThread(
        id="conv123",
        student_id="student123",
        usmos=["MATH.ALG.1"],
        content_id="content456",
        messages=[]
    )
    
    content = ContentResponse(
        content_id="content456",
        usmos=["MATH.ALG.1"],
        problem="Solve for x: x + 5 = 10",
        answer="x = 5",
        explanation="Subtract 5 from both sides to isolate x."
    )
    
    message = StudentMessage(
        conversation_id="conv123",
        content="How do I solve this equation?",
        action="question"
    )
    
    # Mock methods
    with patch.object(conversation_service, "get_thread", return_value=thread), \
         patch.object(conversation_service, "get_content", return_value=content), \
         patch.object(conversation_service, "add_message", return_value=thread), \
         patch.object(tutor_service, "generate_response") as mock_generate:
        
        mock_generate.return_value = TutorMessage(
            conversation_id="conv123",
            content="To solve this equation, subtract 5 from both sides.",
            feedback={"clarity": 0.9}
        )
        
        # Test the method
        result = await conversation_service.handle_student_action(message)
        
        # Assertions
        assert isinstance(result, TutorMessage)
        assert result.conversation_id == "conv123"
        assert "problem" in result.content.lower() or "question" in result.content.lower()