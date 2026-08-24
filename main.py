import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Admin client with service role key to bypass email confirmation and rate limits
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

app = FastAPI(title="Supabase Auth API")

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthSchema):
    try:
        # Admin create_user auto-confirms the email immediately
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )