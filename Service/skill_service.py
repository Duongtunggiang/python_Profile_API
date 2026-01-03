from fastapi import HTTPException
from Entity.skill import CreateSkillRequest, UpdateSkillRequest
from Service.base_service import get_user_and_client, get_public_client

class SkillService:
    @staticmethod
    async def create_skill(data: CreateSkillRequest, token: str):
        """Tạo skill mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            response = client.table("skills").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create skill")
            return {"status": "success", "message": "Skill created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create skill: {str(e)}")
    
    @staticmethod
    async def get_skills(token: str):
        """Lấy tất cả skills của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("skills").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get skills: {str(e)}")
    
    @staticmethod
    async def get_skill(skill_id: str, token: str):
        """Lấy skill theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("skills").select("*").eq("id", skill_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Skill not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get skill: {str(e)}")
    
    @staticmethod
    async def update_skill(skill_id: str, data: UpdateSkillRequest, token: str):
        """Cập nhật skill"""
        try:
            user_id, client = get_user_and_client(token)
            update_data = data.model_dump(exclude_none=True)
            response = client.table("skills").update(update_data).eq("id", skill_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Skill not found")
            return {"status": "success", "message": "Skill updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update skill: {str(e)}")
    
    @staticmethod
    async def delete_skill(skill_id: str, token: str):
        """Xóa skill"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("skills").delete().eq("id", skill_id).eq("profile_id", user_id).execute()
            return {"status": "success", "message": "Skill deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete skill: {str(e)}")
    
    @staticmethod
    async def get_public_skills(user_id: str):
        """Lấy tất cả skills public của user (không cần token)"""
        try:
            client = get_public_client()
            response = client.table("skills").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public skills: {str(e)}")

