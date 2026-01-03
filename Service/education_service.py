from fastapi import HTTPException
from Entity.education import CreateEducationRequest, UpdateEducationRequest
from Service.base_service import get_user_and_client, serialize_dates


class EducationService:
    @staticmethod
    async def create_education(data: CreateEducationRequest, token: str):
        """Tạo education mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            # Serialize date objects thành ISO format strings
            insert_data = serialize_dates(insert_data)
            response = client.table("educations").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create education")
            return {"status": "success", "message": "Education created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create education: {str(e)}")
    
    @staticmethod
    async def get_educations(token: str):
        """Lấy tất cả educations của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("educations").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get educations: {str(e)}")
    
    @staticmethod
    async def get_education(education_id: str, token: str):
        """Lấy education theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("educations").select("*").eq("id", education_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Education not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get education: {str(e)}")
    
    @staticmethod
    async def update_education(education_id: str, data: UpdateEducationRequest, token: str):
        """Cập nhật education"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("educations").select("id").eq("id", education_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Education not found")
            
            update_data = data.model_dump(exclude_none=True)
            # Serialize date objects thành ISO format strings
            update_data = serialize_dates(update_data)
            response = client.table("educations").update(update_data).eq("id", education_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update education")
            return {"status": "success", "message": "Education updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update education: {str(e)}")
    
    @staticmethod
    async def delete_education(education_id: str, token: str):
        """Xóa education"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("educations").select("id").eq("id", education_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Education not found")
            
            response = client.table("educations").delete().eq("id", education_id).execute()
            return {"status": "success", "message": "Education deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete education: {str(e)}")
    
    @staticmethod
    async def get_public_educations(user_id: str):
        """Lấy tất cả educations public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            response = client.table("educations").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public educations: {str(e)}")

