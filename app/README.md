# AI Tutor Chat Conversation System

This module implements a chat conversation system between a Student and an AI Tutor.

## Overview

The system allows students to interact with an AI tutor to get help with educational content. The conversation is based on specific USMOS (Universal Standards for Mathematical and Other Subjects) and associated content.

## Components

### Models

- `StudentMessage`: Represents a message from a student with actions like question, answer, chat, or regenerate
- `TutorMessage`: Represents a response from the AI tutor
- `ConversationThread`: Represents a conversation thread with messages
- `ContentResponse`: Represents educational content with problem, answer, and explanation

### Services

- `C3Service`: Retrieves content based on USMOS from the C3 service
- `TutorService`: Generates AI tutor responses using DSPy
- `ConversationService`: Manages conversation threads and handles student actions

### API Endpoints

- `POST /chat/start`: Start a new conversation based on USMOS
- `POST /chat/message`: Send a message to the conversation
- `POST /chat/regenerate`: Regenerate the last tutor response
- `GET /chat/conversation/{conversation_id}`: Get a conversation by ID

## Data Flow

1. A conversation is started by providing a list of USMOS
2. The system retrieves content from the C3 service based on the USMOS
3. A conversation thread is created for each piece of content
4. The student can send messages with different actions (question, answer, chat)
5. The AI tutor generates responses based on the student's messages and the content
6. The conversation is stored in Redis using redis-om

## Technologies Used

- FastAPI: Web framework for building the API
- Pydantic: Data validation and serialization
- Redis-OM: Object mapping for Redis
- DSPy: Framework for building AI applications