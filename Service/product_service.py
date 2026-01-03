from fastapi import HTTPException
from Entity.product import CreateProductRequest, UpdateProductRequest
from Service.base_service import get_user_and_client, serialize_dates


class ProductService:
    @staticmethod
    async def create_product(data: CreateProductRequest, token: str):
        """Tạo product mới"""
        try:
            user_id, client = get_user_and_client(token)
            insert_data = data.model_dump()
            insert_data["profile_id"] = user_id
            insert_data = serialize_dates(insert_data)
            response = client.table("products").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create product")
            return {"status": "success", "message": "Product created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")
    
    @staticmethod
    async def get_products(token: str):
        """Lấy tất cả products của user"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("products").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get products: {str(e)}")
    
    @staticmethod
    async def get_product(product_id: str, token: str):
        """Lấy product theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            response = client.table("products").select("*").eq("id", product_id).eq("profile_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Product not found")
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get product: {str(e)}")
    
    @staticmethod
    async def update_product(product_id: str, data: UpdateProductRequest, token: str):
        """Cập nhật product"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("products").select("id").eq("id", product_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Product not found")
            
            update_data = data.model_dump(exclude_none=True)
            update_data = serialize_dates(update_data)
            response = client.table("products").update(update_data).eq("id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update product")
            return {"status": "success", "message": "Product updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")
    
    @staticmethod
    async def delete_product(product_id: str, token: str):
        """Xóa product"""
        try:
            user_id, client = get_user_and_client(token)
            check = client.table("products").select("id").eq("id", product_id).eq("profile_id", user_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Product not found")
            
            response = client.table("products").delete().eq("id", product_id).execute()
            return {"status": "success", "message": "Product deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")
    
    @staticmethod
    async def get_public_products(user_id: str):
        """Lấy tất cả products public của user (không cần token)"""
        try:
            from Service.base_service import get_public_client
            client = get_public_client()
            response = client.table("products").select("*").eq("profile_id", user_id).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public products: {str(e)}")

