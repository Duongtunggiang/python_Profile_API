from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Trên Vercel không gọi load_dotenv() để tránh [Errno 16] Device or resource busy
# (biến môi trường đã được inject sẵn; load_dotenv() đọc file .env có thể gây lỗi trên serverless)
if os.getenv("VERCEL") != "1":
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ruejwdwmbxsayfmcqqxv.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY

# Global client — trên Vercel không tạo lúc import để tránh [Errno 16] lúc cold start
supabase: Client = None
IS_VERCEL = os.getenv("VERCEL") == "1"

if not IS_VERCEL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to create Supabase client: {e}")
        print("Please check your SUPABASE_ANON_KEY in .env file")
        print("Get it from: Supabase Dashboard > Settings > API > Project API keys")
elif IS_VERCEL and not SUPABASE_KEY:
    print("SUPABASE_ANON_KEY/SUPABASE_SERVICE_ROLE_KEY not set on Vercel")
elif not SUPABASE_KEY:
    print("SUPABASE_ANON_KEY not found in .env file")
    print("Please add it from: Supabase Dashboard > Settings > API")


def get_supabase_client() -> Client:
    global supabase
    if supabase is not None:
        return supabase
    if not SUPABASE_KEY:
        raise Exception(
            "Supabase client is not initialized.\n"
            "Please add SUPABASE_ANON_KEY to your .env file.\n"
            "Get it from: Supabase Dashboard > Settings > API > Project API keys"
        )
    # Trên Vercel: tạo client lần đầu khi có request (lazy init)
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        raise Exception(f"Failed to create Supabase client: {e}")

