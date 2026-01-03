from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ruejwdwmbxsayfmcqqxv.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY

# Create Supabase client
supabase: Client = None
if SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to create Supabase client: {e}")
        print("Please check your SUPABASE_ANON_KEY in .env file")
        print("Get it from: Supabase Dashboard > Settings > API > Project API keys")
else:
    print("SUPABASE_ANON_KEY not found in .env file")
    print("Please add it from: Supabase Dashboard > Settings > API")

def get_supabase_client():
    if supabase is None:
        raise Exception(
            "Supabase client is not initialized.\n"
            "Please add SUPABASE_ANON_KEY to your .env file.\n"
            "Get it from: Supabase Dashboard > Settings > API > Project API keys"
        )
    return supabase

