import uvicorn
from app import app

if __name__ == "__main__":
    print("Starting Quantitative Finance Poker Training API...")
    print("Backend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 