from fastapi import HTTPException
from Entity.achievement import CreateAchievementRequest, UpdateAchievementRequest
from Service.base_service import get_user_and_client, serialize_dates


class AchievementService:
    @staticmethod
    async def create_achievement(data: CreateAchievementRequest, token: str):
        """Tạo achievement mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            insert_data = serialize_dates(insert_data)
            response = client.table("achievements").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create achievement")
            return {"status": "success", "message": "Achievement created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create achievement: {str(e)}")
    
    @staticmethod
    async def get_achievements(token: str):
        """Lấy tất cả achievements của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("achievements").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get achievements: {str(e)}")
    
    @staticmethod
    async def get_achievement(achievement_id: str, token: str):
        """Lấy achievement theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("achievements").select("*").eq("id", achievement_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Achievement not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get achievement: {str(e)}")
    
    @staticmethod
    async def update_achievement(achievement_id: str, data: UpdateAchievementRequest, token: str):
        """Cập nhật achievement"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("achievements").select("id").eq("id", achievement_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Achievement not found")
            
            update_data = data.model_dump(exclude_none=True)
            update_data = serialize_dates(update_data)
            response = client.table("achievements").update(update_data).eq("id", achievement_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update achievement")
            return {"status": "success", "message": "Achievement updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update achievement: {str(e)}")
    
    @staticmethod
    async def delete_achievement(achievement_id: str, token: str):
        """Xóa achievement"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("achievements").select("id").eq("id", achievement_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Achievement not found")
            
            response = client.table("achievements").delete().eq("id", achievement_id).execute()
            return {"status": "success", "message": "Achievement deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete achievement: {str(e)}")
    
    @staticmethod
    async def get_public_achievements(user_id: str):
        """Lấy tất cả achievements public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            response = client.table("achievements").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public achievements: {str(e)}")

