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

# Sử dụng Mangum adapter để wrap FastAPI app cho Vercel
# Mangum chuyển đổi ASGI app (FastAPI) thành AWS Lambda handler format
# mà Vercel Python runtime có thể sử dụng
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    print("Successfully created Mangum handler")
except Exception as e:
    print(f"Failed to create Mangum handler: {e}")
    # Fallback: export app directly (may not work on all Vercel versions)
    handler = app
    print("Falling back to direct app export")
