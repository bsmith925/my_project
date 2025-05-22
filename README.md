# AI Tutor Chat System

A test-driven implementation of a chat conversation system between a Student and an AI-Tutor.

## Installation

```bash
uv pip install -e .
```

## Features

- Chat conversation between a Student and an AI-Tutor
- Content retrieval based on USMOS (Universal Standard for Mathematical Object Specification)
- Conversation persistence using Redis
- AI-powered tutor responses using DSPy
- RESTful API endpoints for chat functionality

## Project Structure

- `app/models/chat.py`: Data models for the chat system
- `app/services/c3.py`: Service for content retrieval
- `app/services/tutor.py`: Service for AI response generation
- `app/services/conversation.py`: Service for conversation management
- `app/routers/chat/endpoints.py`: API endpoints for chat functionality
- `tests/`: Test files for models, services, and API

## Development

This project uses [uv](https://github.com/astral-sh/uv) for package management.

### Setup Development Environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest
```

### Running the Application

```bash
python run.py
```

## API Endpoints

- `POST /chat/start`: Start a new conversation with USMOS
- `POST /chat/message`: Send a message to the AI-Tutor
- `POST /chat/regenerate`: Regenerate the tutor's response
- `GET /chat/conversation/{conversation_id}`: Get a conversation by ID

## License

This project is licensed under the MIT License - see the LICENSE file for details.