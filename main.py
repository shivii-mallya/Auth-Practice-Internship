import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends, status
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

app = FastAPI(title="Supabase Auth API")

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

# --- AUTH DEPENDENCY (REUSABLE GUARD) ---

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    
    token = authorization.split(" ")[1]
    
    try:
        user_response = supabase.auth.get_user(token)
        # user_response.user contains the User object
        return {"user": user_response.user, "token": token}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )

# --- STAGE 1 ROUTES ---

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
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

@app.post("/auth/login")
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

# --- STAGE 2 & 4 PROTECTED ROUTES ---

@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def protected_profile(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard")
def protected_dashboard(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "message": f"Welcome to your private dashboard, {user.email}!",
        "status": "Active VIP Session"
    }


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(auth_data: dict = Depends(get_current_user)):
    try:
        # In the Supabase Python SDK, sign_out invalidates the current session
        supabase.auth.sign_out()
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))