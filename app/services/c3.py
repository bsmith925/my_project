"""C3 service for retrieving content based on USMOS."""
import httpx
from typing import List
import logging

from app.config.settings import settings
from app.models.chat import UsmosRequest, ContentResponse

logger = logging.getLogger(__name__)


class C3Service:
    """Service for interacting with the C3 API."""
    
    def __init__(self):
        """Initialize the C3 service."""
        self.base_url = settings.C3_API_URL
        self.api_key = settings.C3_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add API key to headers if available
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def get_content(self, request: UsmosRequest) -> List[ContentResponse]:
        """Get content based on USMOS.
        
        Args:
            request: USMOS request
            
        Returns:
            List of content responses
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/content",
                    params={"usmos": ",".join(request.usmos)},
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                content_data = response.json()
                return [ContentResponse(**item) for item in content_data]
        except httpx.HTTPError as e:
            logger.error(f"Error retrieving content from C3: {e}")
            # In a real application, you might want to handle different types of errors differently
            raise
            
    async def get_mock_content(self, usmos: List[str]) -> List[ContentResponse]:
        """
        Get mock content for testing.
        
        Args:
            usmos: List of USMOS to retrieve content for.
            
        Returns:
            List of ContentResponse objects.
        """
        # Mock data for different USMOS
        mock_data = {
            "MATH.ALG.1": ContentResponse(
                content_id="content123",
                usmos=["MATH.ALG.1"],
                problem="Solve for x: x + 5 = 10",
                answer="x = 5",
                explanation="Subtract 5 from both sides to isolate x."
            ),
            "MATH.ALG.2": ContentResponse(
                content_id="content456",
                usmos=["MATH.ALG.2"],
                problem="Solve the system of equations: x + y = 10, x - y = 4",
                answer="x = 7, y = 3",
                explanation="Add the equations to eliminate y and solve for x, then substitute to find y."
            ),
            "SCIENCE.PHYS.1": ContentResponse(
                content_id="content789",
                usmos=["SCIENCE.PHYS.1"],
                problem="A ball is thrown upward with an initial velocity of 20 m/s. How high will it go?",
                answer="20.4 meters",
                explanation="Use the formula h = v²/(2g) where g = 9.8 m/s²."
            )
        }
        
        # Return content for requested USMOS
        result = []
        for usmo in usmos:
            if usmo in mock_data:
                result.append(mock_data[usmo])
        
        return result


# Singleton instance
c3_service = C3Service()