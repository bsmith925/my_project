import asyncio
import logging
from typing import List, Type

from redis_om import HashModel

from app.models.chat import ConversationThread

logger = logging.getLogger(__name__)

# List of all Redis-OM models to create indices for
MODELS: List[Type[HashModel]] = [
    ConversationThread,
]


async def init_redis_models() -> None:
    """Initialize Redis models by creating indices."""
    for model in MODELS:
        try:
            model.Meta.database.ping()
            logger.info(f"Creating index for {model.__name__}")
            await model.create_index()
        except Exception as e:
            logger.error(f"Failed to create index for {model.__name__}: {e}")
            raise


if __name__ == "__main__":
    """Run this script to initialize Redis models."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_redis_models())