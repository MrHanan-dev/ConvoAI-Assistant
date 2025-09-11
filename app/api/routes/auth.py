"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login"""
    try:
        from app.services.auth_manager import AuthManager
        from app.models.user import User
        from app.core.database import get_db
        
        auth_manager = AuthManager()
        
        # For demo purposes, create a mock user authentication
        # In production, this would query the database
        if request.email == "demo@example.com" and request.password == "demo123":
            # Create access token
            token_data = {"sub": request.email, "user_id": "demo_user_123"}
            access_token = auth_manager.create_access_token(token_data)
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": "demo_user_123",
                    "email": request.email,
                    "first_name": "Demo",
                    "last_name": "User",
                    "plan": "pro"
                }
            )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Logged out successfully"}
