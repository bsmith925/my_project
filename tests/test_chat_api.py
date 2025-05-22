"""Tests for chat conversation API endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.chat import (
    UsmosRequest,
    ContentResponse,
    ConversationThread,
    StudentMessage,
    TutorMessage
)
from app.services.c3 import C3Service
from app.services.conversation import ConversationService
from app.db.redis_client import RedisClient


# Mock Redis client and other services before creating TestClient
with patch("app.db.redis_client.RedisClient.get_instance") as mock_redis_instance, \
     patch("app.db.redis_client.RedisClient.get_om_connection") as mock_redis_om, \
     patch("app.db.init_db.init_redis_models") as mock_init_redis, \
     patch("app.services.tutor.tutor_service") as mock_tutor_service:
    # Mock Redis ping method
    mock_redis_instance.return_value.ping.return_value = True
    mock_redis_om.return_value.ping.return_value = True
    mock_init_redis.return_value = None
    
    # Mock tutor service
    mock_tutor_service.generate_response.return_value = TutorMessage(
        conversation_id="conv123",
        content="This is a mock tutor response",
        feedback={"clarity": 0.9}
    )
    
    # Create test client
    client = TestClient(app)


@pytest.fixture
def mock_c3_service():
    """Mock C3Service."""
    with patch("app.routers.chat.endpoints.c3_service") as mock:
        yield mock


@pytest.fixture
def mock_conversation_service():
    """Mock ConversationService."""
    with patch("app.routers.chat.endpoints.conversation_service") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_redis_models():
    """Mock Redis models."""
    with patch("app.models.chat.ConversationThreadRedis") as mock_thread_redis:
        # Mock save method
        mock_thread_redis.return_value.save.return_value = None
        # Mock get method
        mock_thread_redis.get.return_value = None
        yield mock_thread_redis


def test_start_conversation(mock_c3_service, mock_conversation_service):
    """Test the start_conversation endpoint."""
    # Mock data
    usmos_request = UsmosRequest(usmos=["MATH.ALG.1"])
    content_responses = [
        ContentResponse(
            content_id="content123",
            usmos=["MATH.ALG.1"],
            problem="Solve for x: x + 5 = 10",
            answer="x = 5",
            explanation="Subtract 5 from both sides to isolate x."
        )
    ]
    thread = ConversationThread(
        id="conv123",
        student_id="student123",
        usmos=["MATH.ALG.1"],
        content_id="content123",
        messages=[]
    )
    
    # Mock service methods
    mock_c3_service.get_mock_content.return_value = content_responses
    mock_conversation_service.create_thread.return_value = thread
    mock_conversation_service.start_conversation.return_value = {
        "threads": [thread],
        "contents": content_responses
    }
    
    # Make the request
    response = client.post("/chat/start?student_id=student123", json={"usmos": ["MATH.ALG.1"]})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["threads"][0]["id"] == "conv123"
    assert response.json()["threads"][0]["content_id"] == "content123"
    assert response.json()["contents"][0]["content_id"] == "content123"
    assert response.json()["contents"][0]["problem"] == "Solve for x: x + 5 = 10"


def test_send_message(mock_conversation_service):
    """Test the send_message endpoint."""
    # Mock data
    student_message = StudentMessage(
        conversation_id="conv123",
        content="How do I solve this equation?",
        action="question"
    )
    tutor_response = TutorMessage(
        conversation_id="conv123",
        content="To solve this equation, subtract 5 from both sides.",
        feedback={"clarity": 0.9}
    )
    
    # Mock service methods
    mock_conversation_service.handle_student_action.return_value = tutor_response
    
    # Make the request
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": "conv123",
            "content": "How do I solve this equation?",
            "action": "question"
        }
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["conversation_id"] == "conv123"
    assert "subtract 5 from both sides" in response.json()["content"].lower()


def test_regenerate_response(mock_conversation_service):
    """Test the regenerate_response endpoint."""
    # Mock data
    tutor_response = TutorMessage(
        conversation_id="conv123",
        content="Let me explain this differently. Subtract 5 from both sides of the equation.",
        feedback={"clarity": 0.95}
    )
    
    # Mock service methods
    mock_conversation_service.regenerate_tutor_response.return_value = tutor_response
    
    # Make the request
    response = client.post("/chat/regenerate", json={"conversation_id": "conv123"})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["conversation_id"] == "conv123"
    assert "explain this differently" in response.json()["content"].lower()


def test_get_conversation(mock_conversation_service):
    """Test the get_conversation endpoint."""
    # Mock data
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
            ),
            TutorMessage(
                conversation_id="conv123",
                content="To solve x + 5 = 10, subtract 5 from both sides.",
                feedback={"clarity": 0.9}
            )
        ]
    )
    
    # Mock service methods
    mock_conversation_service.get_thread.return_value = thread
    
    # Make the request
    response = client.get("/chat/conversation/conv123")
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == "conv123"
    assert len(response.json()["messages"]) == 2
    assert response.json()["messages"][0]["content"] == "How do I solve x + 5 = 10?"
    assert response.json()["messages"][1]["content"] == "To solve x + 5 = 10, subtract 5 from both sides."