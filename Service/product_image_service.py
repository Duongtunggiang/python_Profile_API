from fastapi import HTTPException
from Entity.product_image import CreateProductImageRequest, UpdateProductImageRequest
from Service.base_service import get_user_and_client, serialize_dates


class ProductImageService:
    @staticmethod
    async def create_product_image(data: CreateProductImageRequest, token: str):
        """Tạo product image mới"""
        try:
            user_id, client = get_user_and_client(token)
            # Kiểm tra product thuộc về user
            product = client.table("products").select("profile_id").eq("id", data.product_id).execute()
            if not product.data or product.data[0]["profile_id"] != user_id:
                raise HTTPException(status_code=404, detail="Product not found")
            
            insert_data = data.model_dump()
            insert_data = serialize_dates(insert_data)
            response = client.table("productImages").insert(insert_data).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create product image")
            return {"status": "success", "message": "Product image created successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create product image: {str(e)}")
    
    @staticmethod
    async def get_product_images(token: str, product_id: str = None):
        """Lấy tất cả product images của user, hoặc của một product cụ thể"""
        try:
            user_id, client = get_user_and_client(token)
            if product_id:
                # Kiểm tra product thuộc về user
                product = client.table("products").select("profile_id").eq("id", product_id).execute()
                if not product.data or product.data[0]["profile_id"] != user_id:
                    raise HTTPException(status_code=404, detail="Product not found")
                response = client.table("productImages").select("*").eq("product_id", product_id).execute()
            else:
                # Lấy tất cả product images của user (thông qua products)
                products = client.table("products").select("id").eq("profile_id", user_id).execute()
                product_ids = [p["id"] for p in (products.data or [])]
                if not product_ids:
                    return {"status": "success", "data": [], "count": 0}
                response = client.table("productImages").select("*").in_("product_id", product_ids).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get product images: {str(e)}")
    
    @staticmethod
    async def get_product_image(image_id: str, token: str):
        """Lấy product image theo ID"""
        try:
            user_id, client = get_user_and_client(token)
            # Kiểm tra image thuộc về product của user
            image = client.table("productImages").select("product_id").eq("id", image_id).execute()
            if not image.data:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            product = client.table("products").select("profile_id").eq("id", image.data[0]["product_id"]).execute()
            if not product.data or product.data[0]["profile_id"] != user_id:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            response = client.table("productImages").select("*").eq("id", image_id).execute()
            return {"status": "success", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get product image: {str(e)}")
    
    @staticmethod
    async def update_product_image(image_id: str, data: UpdateProductImageRequest, token: str):
        """Cập nhật product image"""
        try:
            user_id, client = get_user_and_client(token)
            # Kiểm tra image thuộc về product của user
            image = client.table("productImages").select("product_id").eq("id", image_id).execute()
            if not image.data:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            product = client.table("products").select("profile_id").eq("id", image.data[0]["product_id"]).execute()
            if not product.data or product.data[0]["profile_id"] != user_id:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            update_data = data.model_dump(exclude_none=True)
            update_data = serialize_dates(update_data)
            response = client.table("productImages").update(update_data).eq("id", image_id).execute()
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update product image")
            return {"status": "success", "message": "Product image updated successfully", "data": response.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update product image: {str(e)}")
    
    @staticmethod
    async def delete_product_image(image_id: str, token: str):
        """Xóa product image"""
        try:
            user_id, client = get_user_and_client(token)
            # Kiểm tra image thuộc về product của user
            image = client.table("productImages").select("product_id").eq("id", image_id).execute()
            if not image.data:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            product = client.table("products").select("profile_id").eq("id", image.data[0]["product_id"]).execute()
            if not product.data or product.data[0]["profile_id"] != user_id:
                raise HTTPException(status_code=404, detail="Product image not found")
            
            response = client.table("productImages").delete().eq("id", image_id).execute()
            return {"status": "success", "message": "Product image deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete product image: {str(e)}")
    
    @staticmethod
    async def get_public_product_images(user_id: str, product_id: str = None):
        """Lấy tất cả product images public của user (không cần token)"""
        try:
            from Connection import connection
            client = connection.get_supabase_client()
            if product_id:
                response = client.table("productImages").select("*").eq("product_id", product_id).execute()
            else:
                products = client.table("products").select("id").eq("profile_id", user_id).execute()
                product_ids = [p["id"] for p in (products.data or [])]
                if not product_ids:
                    return {"status": "success", "data": [], "count": 0}
                response = client.table("productImages").select("*").in_("product_id", product_ids).execute()
            return {"status": "success", "data": response.data if response.data else [], "count": len(response.data) if response.data else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get public product images: {str(e)}")

