from fastapi import HTTPException
from Connection import connection
from Entity.auth import LoginRequest, RegisterRequest


class AuthService:
    @staticmethod
    async def login(credentials: LoginRequest):
        """Đăng nhập với email và password"""
        try:
            client = connection.get_supabase_client()
            
            # Xác thực người dùng với Supabase Auth
            response = client.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if response.user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            return {
                "status": "success",
                "message": "Login successful",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                },
                "access_token": response.session.access_token if response.session else None,
            }
        except Exception as e:
            error_message = str(e)
            if "Invalid login credentials" in error_message:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            raise HTTPException(status_code=500, detail=f"Login failed: {error_message}")
    
    @staticmethod
    async def register(user_data: RegisterRequest):
        """Đăng ký tài khoản mới"""
        try:
            client = connection.get_supabase_client()
            
            # Tạo tài khoản mới
            response = client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if response.user is None:
                raise HTTPException(status_code=400, detail="Registration failed")
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                }
            }
        except Exception as e:
            error_message = str(e)
            if "User already registered" in error_message or "already registered" in error_message.lower():
                raise HTTPException(status_code=400, detail="Email already registered")
            raise HTTPException(status_code=500, detail=f"Registration failed: {error_message}")
    
    @staticmethod
    async def get_current_user(token: str):
        """Lấy thông tin user hiện tại từ access token"""
        try:
            client = connection.get_supabase_client()
            
            # Lấy thông tin user từ token
            user_response = client.auth.get_user(token)
            
            if user_response.user is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return {
                "status": "success",
                "user": {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "created_at": user_response.user.created_at,
                }
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

