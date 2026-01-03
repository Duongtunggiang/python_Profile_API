from fastapi import HTTPException
from Entity.language import CreateLanguageRequest, UpdateLanguageRequest
from Service.base_service import get_user_and_client


class LanguageService:
    @staticmethod
    async def create_language(data: CreateLanguageRequest, token: str):
        """Tạo language mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            response = client.table("languages").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create language")
            return {"status": "success", "message": "Language created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create language: {str(e)}")
    
    @staticmethod
    async def get_languages(token: str):
        """Lấy tất cả languages của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("languages").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")
    
    @staticmethod
    async def get_language(language_id: str, token: str):
        """Lấy language theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("languages").select("*").eq("id", language_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Language not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get language: {str(e)}")
    
    @staticmethod
    async def update_language(language_id: str, data: UpdateLanguageRequest, token: str):
        """Cập nhật language"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("languages").select("id").eq("id", language_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Language not found")
            
            update_data = data.model_dump(exclude_none=True)
            response = client.table("languages").update(update_data).eq("id", language_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update language")
            return {"status": "success", "message": "Language updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update language: {str(e)}")
    
    @staticmethod
    async def delete_language(language_id: str, token: str):
        """Xóa language"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("languages").select("id").eq("id", language_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Language not found")
            
            response = client.table("languages").delete().eq("id", language_id).execute()
            return {"status": "success", "message": "Language deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete language: {str(e)}")
    
    @staticmethod
    async def get_public_languages(user_id: str):
        """Lấy tất cả languages public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            response = client.table("languages").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public languages: {str(e)}")

