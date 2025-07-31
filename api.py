from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
from dotenv import load_dotenv
from news_handler import TelegramNewsHandler

# Load environment variables
load_dotenv()

app = FastAPI(title="Telegram News API", description="API to fetch posts from Telegram channels")

# Security
security = HTTPBearer()

# Pydantic models
class TelegramRequest(BaseModel):
    channels: List[str]
    duration_hours: Optional[int] = 24

class TelegramResponse(BaseModel):
    success: bool
    data: dict
    message: str

# Authentication function
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API token"""
    token = credentials.credentials
    expected_token = os.getenv('API_TOKEN')
    
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API token not configured"
        )
    
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )
    
    return token

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Telegram News API is running"}

@app.post("/fetch-news", response_model=TelegramResponse)
async def get_telegram_posts(
    request: TelegramRequest,
    token: str = Depends(verify_token)
):
    """
    Fetch posts from Telegram channels within specified duration
    
    - **channels**: List of channel usernames or IDs
    - **duration_hours**: Number of hours to look back (default: 24)
    """
    try:
        # Validate input
        if not request.channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one channel must be provided"
            )
        
        if request.duration_hours <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duration must be greater than 0"
            )
        
        # Get Telegram credentials
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        phone = os.getenv('TELEGRAM_PHONE')
        
        if not all([api_id, api_hash, phone]):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram credentials not configured"
            )
        
        # Initialize Telegram handler with session path
        session_path = os.getenv('SESSION_PATH', '/app/sessions')
        handler = TelegramNewsHandler(api_id, api_hash, phone, session_path)
        
        try:
            # Start the client
            await handler.start()
            
            # Get posts from channels
            all_posts = await handler.get_all_channel_posts(
                request.channels, 
                request.duration_hours
            )
            
            return TelegramResponse(
                success=True,
                data=all_posts,
                message=f"Successfully fetched posts from {len(request.channels)} channels"
            )
            
        finally:
            await handler.stop()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 