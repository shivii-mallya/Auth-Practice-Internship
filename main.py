import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

app = FastAPI(
    title="Supabase Auth API",
    description="A secure authentication API built with FastAPI and Supabase",
    version="1.0.0"
)

# 1. Initialize HTTPBearer scheme to trigger the lock icon in Swagger UI
security = HTTPBearer()

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

# --- AUTH DEPENDENCY (UPDATED FOR SWAGGER UI) ---

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # HTTPBearer automatically extracts the token string from "Authorization: Bearer <token>"
    token = credentials.credentials
    
    try:
        user_response = supabase.auth.get_user(token)
        return {"user": user_response.user, "token": token}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )

# --- STAGE 1 ROUTES ---

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def signup(credentials: AuthSchema):
    try:
        res = supabase_admin.auth.admin.create_user({
            "email": credentials.email,
            "password": credentials.password,
            "email_confirm": True
        })
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", tags=["Authentication"])
def login(credentials: AuthSchema):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# --- PUBLIC ROUTES ---

@app.get("/public/info", status_code=status.HTTP_200_OK, tags=["Public"])
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# --- PROTECTED ROUTES ---

@app.get("/protected/profile", tags=["Protected"])
def protected_profile(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard", tags=["Protected"])
def protected_dashboard(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "message": f"Welcome to your private dashboard, {user.email}!",
        "status": "Active VIP Session"
    }

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["Authentication"])
def logout(auth_data: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out(auth_data["token"])
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))