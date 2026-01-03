import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


async def upload_image_to_cloudinary(file_content: bytes, folder: str = "uploads", public_id: str = None):
    """
    Upload ảnh lên Cloudinary
    
    Args:
        file_content: Nội dung file (bytes)
        folder: Thư mục trên Cloudinary (mặc định: "uploads")
        public_id: ID công khai cho file (nếu None sẽ tự động tạo)
    
    Returns:
        dict: Chứa image_url và public_id
    """
    try:
        # Upload lên Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            public_id=public_id,
            resource_type="image",
            overwrite=True,
            invalidate=True
        )
        
        # Lấy URL của ảnh
        image_url = upload_result.get("secure_url") or upload_result.get("url")
        
        return {
            "status": "success",
            "image_url": image_url,
            "public_id": upload_result.get("public_id"),
            "format": upload_result.get("format"),
            "width": upload_result.get("width"),
            "height": upload_result.get("height"),
            "bytes": upload_result.get("bytes")
        }
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")


async def delete_image_from_cloudinary(public_id: str):
    """
    Xóa ảnh khỏi Cloudinary
    
    Args:
        public_id: Public ID của ảnh trên Cloudinary
    
    Returns:
        dict: Kết quả xóa
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return {
            "status": "success" if result.get("result") == "ok" else "failed",
            "result": result
        }
    except Exception as e:
        raise Exception(f"Cloudinary delete failed: {str(e)}")

