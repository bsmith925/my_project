"""Tests for chat conversation models."""
import pytest
from pydantic import ValidationError

from app.models.chat import (
    StudentMessage,
    TutorMessage,
    ConversationThread,
    UsmosRequest,
    ContentResponse,
)


def test_student_message_model():
    """Test the StudentMessage model."""
    # Valid message
    message = StudentMessage(
        conversation_id="conv123",
        content="How do I solve this equation?",
        action="question"
    )
    assert message.conversation_id == "conv123"
    assert message.content == "How do I solve this equation?"
    assert message.action == "question"
    
    # Invalid action
    with pytest.raises(ValidationError):
        StudentMessage(
            conversation_id="conv123",
            content="How do I solve this equation?",
            action="invalid_action"
        )


def test_tutor_message_model():
    """Test the TutorMessage model."""
    message = TutorMessage(
        conversation_id="conv123",
        content="To solve this equation, you need to isolate the variable.",
        feedback={"clarity": 0.9, "helpfulness": 0.85}
    )
    assert message.conversation_id == "conv123"
    assert message.content == "To solve this equation, you need to isolate the variable."
    assert message.feedback["clarity"] == 0.9


def test_conversation_thread_model():
    """Test the ConversationThread model."""
    thread = ConversationThread(
        id="conv123",
        student_id="student123",
        usmos=["MATH.ALG.1", "MATH.ALG.2"],
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
    
    assert thread.id == "conv123"
    assert "MATH.ALG.1" in thread.usmos
    assert len(thread.messages) == 2
    assert isinstance(thread.messages[0], StudentMessage)
    assert isinstance(thread.messages[1], TutorMessage)


def test_usmos_request_model():
    """Test the UsmosRequest model."""
    request = UsmosRequest(usmos=["MATH.ALG.1", "MATH.ALG.2"])
    assert "MATH.ALG.1" in request.usmos
    assert len(request.usmos) == 2
    
    # Empty usmos list should raise validation error
    with pytest.raises(ValidationError):
        UsmosRequest(usmos=[])


def test_content_response_model():
    """Test the ContentResponse model."""
    response = ContentResponse(
        content_id="content123",
        usmos=["MATH.ALG.1"],
        problem="Solve for x: x + 5 = 10",
        answer="x = 5",
        explanation="Subtract 5 from both sides to isolate x."
    )
    
    assert response.content_id == "content123"
    assert response.problem == "Solve for x: x + 5 = 10"
    assert response.answer == "x = 5"