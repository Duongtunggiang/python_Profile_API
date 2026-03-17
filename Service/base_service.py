from fastapi import HTTPException
from supabase import create_client
from Connection import connection
from datetime import date, datetime
from typing import Any, Dict
import os
import time

# Client dùng cho public endpoints (service_role), lazy init + cache để tránh [Errno 16] trên Vercel
_public_client = None


def get_user_and_client(token: str):
    """Verify token và trả về user_id và Supabase client với service_role key"""
    # Verify token và lấy user id
    client_auth = connection.get_supabase_client()
    user_response = client_auth.auth.get_user(token)
    
    if user_response.user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = user_response.user.id
    
    # Dùng service_role key cho backend operations (bypass RLS)
    if connection.SUPABASE_SERVICE_ROLE_KEY:
        client = create_client(connection.SUPABASE_URL, connection.SUPABASE_SERVICE_ROLE_KEY)
    else:
        client = connection.get_supabase_client()
    
    return user_id, client


def serialize_dates(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert date và datetime objects thành ISO format strings cho Supabase"""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, date):
            # Convert date to ISO format string (YYYY-MM-DD)
            serialized[key] = value.isoformat()
        elif isinstance(value, datetime):
            # Convert datetime to ISO format string
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized


def get_public_client():
    """Supabase client với service role key cho public endpoints (lazy init + cache, tránh EBUSY trên Vercel)."""
    global _public_client
    if _public_client is not None:
        return _public_client
    SUPABASE_URL = os.getenv("SUPABASE_URL") or connection.SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or connection.SUPABASE_SERVICE_ROLE_KEY
    if not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_ROLE_KEY not configured")
    for attempt in range(2):
        try:
            _public_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            return _public_client
        except OSError as e:
            if getattr(e, "errno", None) == 16 and attempt == 0:
                time.sleep(0.3)
                continue
            raise HTTPException(status_code=500, detail=f"Failed to create public client: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create public client: {e}")
