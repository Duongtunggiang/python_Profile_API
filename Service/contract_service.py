from fastapi import HTTPException
from Entity.contract import CreateContractRequest, UpdateContractRequest
from Service.base_service import get_user_and_client


class ContractService:
    @staticmethod
    async def create_contract(data: CreateContractRequest, token: str):
        """Tạo contract mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            response = client.table("contracts").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create contract")
            return {"status": "success", "message": "Contract created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create contract: {str(e)}")
    
    @staticmethod
    async def get_contracts(token: str):
        """Lấy tất cả contracts của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("contracts").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get contracts: {str(e)}")
    
    @staticmethod
    async def get_contract(contract_id: str, token: str):
        """Lấy contract theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("contracts").select("*").eq("id", contract_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Contract not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get contract: {str(e)}")
    
    @staticmethod
    async def update_contract(contract_id: str, data: UpdateContractRequest, token: str):
        """Cập nhật contract"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("contracts").select("id").eq("id", contract_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            update_data = data.model_dump(exclude_none=True)
            response = client.table("contracts").update(update_data).eq("id", contract_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update contract")
            return {"status": "success", "message": "Contract updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update contract: {str(e)}")
    
    @staticmethod
    async def delete_contract(contract_id: str, token: str):
        """Xóa contract"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("contracts").select("id").eq("id", contract_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            response = client.table("contracts").delete().eq("id", contract_id).execute()
            return {"status": "success", "message": "Contract deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete contract: {str(e)}")
    
    @staticmethod
    async def get_public_contracts(user_id: str):
        """Lấy tất cả contracts public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            response = client.table("contracts").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public contracts: {str(e)}")

