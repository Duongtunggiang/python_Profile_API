from fastapi import HTTPException
from Entity.image import CreateImageRequest, UpdateImageRequest
from Service.base_service import get_user_and_client


class ImageService:
    @staticmethod
    async def create_image(data: CreateImageRequest, token: str):
        """Tạo image mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            response = client.table("images").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create image")
            return {"status": "success", "message": "Image created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create image: {str(e)}")
    
    @staticmethod
    async def get_images(token: str):
        """Lấy tất cả images của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("images").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get images: {str(e)}")
    
    @staticmethod
    async def get_image(image_id: str, token: str):
        """Lấy image theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("images").select("*").eq("id", image_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Image not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get image: {str(e)}")
    
    @staticmethod
    async def update_image(image_id: str, data: UpdateImageRequest, token: str):
        """Cập nhật image"""
        try:
            user_id, client = get_user_and_client(token)
            # Verify ownership
            check = client.table("images").select("id").eq("id", image_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Image not found")
            
            update_data = data.model_dump(exclude_none=True)
            response = client.table("images").update(update_data).eq("id", image_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update image")
            return {"status": "success", "message": "Image updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update image: {str(e)}")
    
    @staticmethod
    async def delete_image(image_id: str, token: str):
        """Xóa image"""
        try:
            user_id, client = get_user_and_client(token)
            # Verify ownership
            check = client.table("images").select("id").eq("id", image_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Image not found")
            
            response = client.table("images").delete().eq("id", image_id).execute()
            return {"status": "success", "message": "Image deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

    @staticmethod
    async def get_public_images(user_id: str):
        """Lấy tất cả images public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            response = client.table("images").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public images: {str(e)}")

