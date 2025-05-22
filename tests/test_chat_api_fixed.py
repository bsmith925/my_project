"""Tests for chat conversation API endpoints."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


# Create patches for all dependencies
redis_instance_patch = patch("app.db.redis_client.RedisClient.get_instance")
redis_om_patch = patch("app.db.redis_client.RedisClient.get_om_connection")
init_redis_patch = patch("app.db.init_db.init_redis_models")
tutor_service_patch = patch("app.services.tutor.tutor_service")
c3_service_patch = patch("app.routers.chat.endpoints.c3_service")
conversation_service_patch = patch("app.routers.chat.endpoints.conversation_service")
thread_redis_patch = patch("app.models.chat.ConversationThreadRedis")

# Start all patches
mock_redis_instance = redis_instance_patch.start()
mock_redis_om = redis_om_patch.start()
mock_init_redis = init_redis_patch.start()
mock_tutor_service = tutor_service_patch.start()
mock_c3_service = c3_service_patch.start()
mock_conversation_service = conversation_service_patch.start()
mock_thread_redis = thread_redis_patch.start()

# Configure mocks
mock_redis_instance.return_value.ping.return_value = True
mock_redis_om.return_value.ping.return_value = True
mock_init_redis.return_value = None

# Mock tutor service
mock_tutor_service.generate_response = AsyncMock(return_value=TutorMessage(
    conversation_id="conv123",
    content="This is a mock tutor response",
    feedback={"clarity": 0.9}
))

# Create test client
client = TestClient(app)

# Clean up patches after tests
def pytest_sessionfinish(session, exitstatus):
    redis_instance_patch.stop()
    redis_om_patch.stop()
    init_redis_patch.stop()
    tutor_service_patch.stop()
    c3_service_patch.stop()
    conversation_service_patch.stop()
    thread_redis_patch.stop()


def test_start_conversation():
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
    mock_c3_service.get_mock_content = AsyncMock(return_value=content_responses)
    mock_conversation_service.start_conversation = AsyncMock(return_value={
        "threads": [thread],
        "contents": content_responses
    })

    # Make the request
    response = client.post("/chat/start?student_id=student123", json={"usmos": ["MATH.ALG.1"]})

    # Assertions
    assert response.status_code == 200
    assert response.json()["threads"][0]["id"] == "conv123"
    assert response.json()["threads"][0]["content_id"] == "content123"
    assert response.json()["contents"][0]["content_id"] == "content123"
    assert response.json()["contents"][0]["problem"] == "Solve for x: x + 5 = 10"


def test_send_message():
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
    mock_conversation_service.handle_student_action = AsyncMock(return_value=tutor_response)

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


def test_regenerate_response():
    """Test the regenerate_response endpoint."""
    # Mock data
    tutor_response = TutorMessage(
        conversation_id="conv123",
        content="Let me explain this differently. Subtract 5 from both sides of the equation.",
        feedback={"clarity": 0.95}
    )

    # Mock service methods
    mock_conversation_service.regenerate_tutor_response = AsyncMock(return_value=tutor_response)

    # Make the request
    response = client.post("/chat/regenerate", json={"conversation_id": "conv123"})

    # Assertions
    assert response.status_code == 200
    assert response.json()["conversation_id"] == "conv123"
    assert "explain this differently" in response.json()["content"].lower()


def test_get_conversation():
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
    mock_conversation_service.get_thread = AsyncMock(return_value=thread)

    # Make the request
    response = client.get("/chat/conversation/conv123")

    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == "conv123"
    assert len(response.json()["messages"]) == 2
    assert response.json()["messages"][0]["content"] == "How do I solve x + 5 = 10?"
    assert response.json()["messages"][1]["content"] == "To solve x + 5 = 10, subtract 5 from both sides."