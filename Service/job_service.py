from fastapi import HTTPException
from Entity.job import CreateJobRequest, UpdateJobRequest
from Service.base_service import get_user_and_client, serialize_dates


class JobService:
    @staticmethod
    async def create_job(data: CreateJobRequest, token: str):
        """Tạo job mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            # Serialize date objects thành ISO format strings (start_date, end_date là string nên không ảnh hưởng)
            insert_data = serialize_dates(insert_data)
            response = client.table("jobs").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create job")
            return {"status": "success", "message": "Job created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
    
    @staticmethod
    async def get_jobs(token: str):
        """Lấy tất cả jobs của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("jobs").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")
    
    @staticmethod
    async def get_job(job_id: str, token: str):
        """Lấy job theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("jobs").select("*").eq("id", job_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Job not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")
    
    @staticmethod
    async def update_job(job_id: str, data: UpdateJobRequest, token: str):
        """Cập nhật job"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("jobs").select("id").eq("id", job_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Job not found")
            
            update_data = data.model_dump(exclude_none=True)
            # Serialize date objects thành ISO format strings (start_date, end_date là string nên không ảnh hưởng)
            update_data = serialize_dates(update_data)
            response = client.table("jobs").update(update_data).eq("id", job_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update job")
            return {"status": "success", "message": "Job updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")
    
    @staticmethod
    async def delete_job(job_id: str, token: str):
        """Xóa job"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("jobs").select("id").eq("id", job_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Job not found")
            
            response = client.table("jobs").delete().eq("id", job_id).execute()
            return {"status": "success", "message": "Job deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")
    
    @staticmethod
    async def get_public_jobs(user_id: str):
        """Lấy tất cả jobs public của user (không cần token)"""
        try:
            from Service.base_service import get_public_client
            client = get_public_client()
            response = client.table("jobs").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public jobs: {str(e)}")

