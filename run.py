"""Script to run the FastAPI application."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=54550,  # Using the port provided in the runtime information
        reload=True,
        log_level="info",
    )