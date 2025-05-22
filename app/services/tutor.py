"""Tutor service for generating responses."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    import dspy
except ImportError:
    dspy = None

from app.config.settings import settings
from app.models.chat import (
    ConversationThread,
    ContentResponse,
    TutorMessage,
    StudentMessage
)

logger = logging.getLogger(__name__)


class TutorService:
    """Service for generating tutor responses."""
    
    def __init__(self):
        """Initialize the tutor service."""
        self.dspy_configured = False
        
        # Configure DSPy if available
        if dspy is not None:
            try:
                # Configure DSPy with the LLM specified in settings
                if settings.LLM_PROVIDER == "openai":
                    dspy.configure(
                        lm=dspy.OpenAI(
                            model=settings.LLM_MODEL,
                            api_key=settings.OPENAI_API_KEY
                        )
                    )
                    self.dspy_configured = True
                elif settings.LLM_PROVIDER == "anthropic":
                    dspy.configure(
                        lm=dspy.Anthropic(
                            model=settings.LLM_MODEL,
                            api_key=settings.ANTHROPIC_API_KEY
                        )
                    )
                    self.dspy_configured = True
                else:
                    logger.warning(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
            except Exception as e:
                logger.error(f"Failed to configure DSPy: {e}")
        else:
            logger.warning("DSPy not available, using fallback response generation")
    
    async def generate_response(
        self, thread: ConversationThread, content: ContentResponse
    ) -> TutorMessage:
        """Generate a response to the student's message.
        
        Args:
            thread: The conversation thread
            content: The content being discussed
            
        Returns:
            Generated tutor message
        """
        # Get the last student message
        last_message = None
        for message in reversed(thread.messages):
            if isinstance(message, StudentMessage):
                last_message = message
                break
        
        if not last_message:
            # If there's no student message, create a generic introduction
            return TutorMessage(
                conversation_id=thread.id,
                content=f"Let's discuss this problem: {content.problem}. How would you approach solving it?"
            )
        
        # Format conversation history
        conversation_history = self._format_conversation_history(thread.messages)
        
        # Use DSPy if configured, otherwise fall back to rule-based responses
        if self.dspy_configured and dspy is not None:
            response = await self._generate_dspy_response(
                conversation_history, 
                last_message, 
                content
            )
        else:
            # Fall back to rule-based responses
            if last_message.action == "question":
                response = f"That's a good question about '{content.problem}'. The answer is '{content.answer}'. Does that make sense?"
            elif last_message.action == "answer":
                if content.answer.lower() in last_message.content.lower():
                    response = "That's correct! Well done."
                else:
                    response = f"Not quite. The correct answer is '{content.answer}'. Let me explain: {content.explanation or 'Think about it carefully.'}"
            elif last_message.action == "chat":
                response = f"I understand your comment. Let's continue discussing this problem: {content.problem}"
            else:  # regenerate
                response = f"Let me try to explain this differently. The problem is '{content.problem}' and the answer is '{content.answer}'. {content.explanation or ''}"
        
        # Create and return the tutor message
        return TutorMessage(
            conversation_id=thread.id,
            content=response,
            feedback=self._generate_feedback(response)
        )
    
    def _format_conversation_history(self, messages: list) -> str:
        """Format the conversation history.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Formatted conversation history
        """
        history = []
        for message in messages:
            if isinstance(message, StudentMessage):
                history.append(f"Student: {message.content}")
            elif isinstance(message, TutorMessage):
                history.append(f"Tutor: {message.content}")
        
        return "\n".join(history)
    
    async def _generate_dspy_response(
        self, 
        conversation_history: str, 
        last_message: StudentMessage, 
        content: ContentResponse
    ) -> str:
        """Generate a response using DSPy.
        
        Args:
            conversation_history: Formatted conversation history
            last_message: The last student message
            content: The content being discussed
            
        Returns:
            Generated response
        """
        if dspy is None:
            logger.error("DSPy not available but _generate_dspy_response was called")
            return "I'm sorry, I'm having trouble generating a response right now."
        
        try:
            # Define a DSPy program for tutoring
            class TutorProgram(dspy.Module):
                def __init__(self):
                    super().__init__()
                    self.generate = dspy.ChainOfThought("conversation_history, problem, answer, explanation, student_message -> tutor_response")
                
                def forward(self, conversation_history, problem, answer, explanation, student_message):
                    return self.generate(
                        conversation_history=conversation_history,
                        problem=problem,
                        answer=answer,
                        explanation=explanation,
                        student_message=student_message
                    )
            
            # Create and run the program
            program = TutorProgram()
            result = program(
                conversation_history=conversation_history,
                problem=content.problem,
                answer=content.answer,
                explanation=content.explanation or "",
                student_message=last_message.content
            )
            
            return result.tutor_response
        except Exception as e:
            logger.error(f"Error generating DSPy response: {e}")
            # Fall back to a simple response
            return f"I understand your question about {content.problem}. The answer is {content.answer}."

    def _generate_feedback(self, response: str) -> Dict[str, float]:
        """Generate feedback metrics for the tutor's response.
        
        In a real application, this would use a model to evaluate the response.
        For now, we'll return some placeholder values.
        
        Args:
            response: The tutor's response
            
        Returns:
            Feedback metrics
        """
        # This is a placeholder. In a real application, you would use a model to
        # evaluate the response and generate meaningful feedback metrics.
        return {
            "clarity": 0.9,
            "helpfulness": 0.85,
            "engagement": 0.8
        }


# Singleton instance
tutor_service = TutorService()