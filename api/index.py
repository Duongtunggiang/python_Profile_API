import sys
import os
import traceback

# Thêm thư mục gốc vào Python path để import được các module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import app từ main.py với error handling
try:
    from main import app
    print("Successfully imported app from main.py")
except Exception as e:
    print(f"Failed to import app from main.py: {e}")
    print("Traceback:")
    traceback.print_exc()
    raise

# Vercel Python runtime automatically handles ASGI apps (FastAPI)
# Export app directly - no need for Mangum with newer Vercel Python runtime
handler = app
print("Handler exported as FastAPI app (ASGI)")
