from fastapi import HTTPException
from datetime import datetime
from Entity.profile import UpdateProfileRequest
from Service.base_service import get_user_and_client, serialize_dates


class ProfileService:
    @staticmethod
    async def update_profile(profile_data: UpdateProfileRequest, token: str):
        """Cập nhật profile trong bảng duong (id = auth.users.id)"""
        try:
            user_id, client = get_user_and_client(token)
            
            # Chuẩn bị data để update/insert (chỉ lấy các field không None)
            update_data = profile_data.model_dump(exclude_none=True)
            update_data["id"] = user_id
            update_data["update_at"] = datetime.utcnow().isoformat()
            
            # Serialize date objects thành ISO format strings
            update_data = serialize_dates(update_data)
            
            # Dùng upsert để insert hoặc update (dựa trên id)
            response = client.table("duong").upsert(update_data, on_conflict="id").execute()
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update profile")
            
            return {
                "status": "success",
                "message": "Profile updated successfully",
                "data": response.data[0] if response.data else None
            }
        except HTTPException:
            raise
        except Exception as e:
            error_message = str(e)
            if "Invalid token" in error_message or "JWT" in error_message or "unauthorized" in error_message.lower() or "permission denied" in error_message.lower():
                raise HTTPException(status_code=401, detail="Invalid token or insufficient permissions")
            raise HTTPException(status_code=500, detail=f"Failed to update profile: {error_message}")
    
    @staticmethod
    async def get_profile(token: str):
        """Lấy profile từ bảng duong (id = auth.users.id)"""
        try:
            user_id, client = get_user_and_client(token)
            
            # Lấy profile từ bảng duong (dùng service_role key để bypass RLS)
            response = client.table("duong").select("*").eq("id", user_id).execute()
            
            if not response.data:
                return {
                    "status": "success",
                    "message": "Profile not found",
                    "data": None
                }
            
            return {
                "status": "success",
                "data": response.data[0]
            }
        except HTTPException:
            raise
        except Exception as e:
            error_message = str(e)
            if "Invalid token" in error_message or "JWT" in error_message:
                raise HTTPException(status_code=401, detail="Invalid token")
            raise HTTPException(status_code=500, detail=f"Failed to get profile: {error_message}")

    @staticmethod
    async def get_public_profile(user_id: str = None):
        """Lấy profile public (không cần token) - lấy profile đầu tiên hoặc theo user_id"""
        try:
            # Tạo client mới với service role key để bypass RLS
            from Service.base_service import get_public_client
            client = get_public_client()
            
            if user_id:
                response = client.table("duong").select("*").eq("id", user_id).execute()
            else:
                # Lấy profile đầu tiên có dữ liệu
                response = client.table("duong").select("*").limit(1).execute()
            
            if not response.data:
                return {
                    "status": "success",
                    "message": "Profile not found",
                    "data": None
                }
            
            return {
                "status": "success",
                "data": response.data[0]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public profile: {str(e)}")

