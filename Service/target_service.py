from fastapi import HTTPException
from Entity.target import CreateTargetRequest, UpdateTargetRequest
from Service.base_service import get_user_and_client, get_public_client

class TargetService:
    @staticmethod
    async def create_target(data: CreateTargetRequest, token: str):
        """Tạo target mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            response = client.table("target").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create target")
            return {"status": "success", "message": "Target created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create target: {str(e)}")
    
    @staticmethod
    async def get_targets(token: str):
        """Lấy tất cả targets của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("target").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get targets: {str(e)}")
    
    @staticmethod
    async def get_target(target_id: str, token: str):
        """Lấy target theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("target").select("*").eq("id", target_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Target not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get target: {str(e)}")
    
    @staticmethod
    async def update_target(target_id: str, data: UpdateTargetRequest, token: str):
        """Cập nhật target"""
        try:
            user_id, client = get_user_and_client(token)
            update_data = data.model_dump(exclude_none=True)
            response = client.table("target").update(update_data).eq("id", target_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Target not found")
            return {"status": "success", "message": "Target updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update target: {str(e)}")
    
    @staticmethod
    async def delete_target(target_id: str, token: str):
        """Xóa target"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("target").delete().eq("id", target_id).eq("profile_id", user_id).execute()
            return {"status": "success", "message": "Target deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete target: {str(e)}")
    
    @staticmethod
    async def get_public_targets(user_id: str):
        """Lấy tất cả targets public của user (không cần token)"""
        try:
            client = get_public_client()
            response = client.table("target").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public targets: {str(e)}")

