from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from pathlib import Path
from Connection import connection
from Service.cloudinary_service import upload_image_to_cloudinary
from Entity.auth import LoginRequest, RegisterRequest
from Entity.profile import UpdateProfileRequest
from Entity.image import CreateImageRequest, UpdateImageRequest
from Entity.education import CreateEducationRequest, UpdateEducationRequest
from Entity.job import CreateJobRequest, UpdateJobRequest
from Entity.language import CreateLanguageRequest, UpdateLanguageRequest
from Entity.contract import CreateContractRequest, UpdateContractRequest
from Entity.achievement import CreateAchievementRequest, UpdateAchievementRequest
from Entity.product import CreateProductRequest, UpdateProductRequest
from Entity.product_image import CreateProductImageRequest, UpdateProductImageRequest
from Entity.skill import CreateSkillRequest, UpdateSkillRequest
from Entity.target import CreateTargetRequest, UpdateTargetRequest
from Service.auth_service import AuthService
from Service.profile_service import ProfileService
from Service.image_service import ImageService
from Service.education_service import EducationService
from Service.job_service import JobService
from Service.language_service import LanguageService
from Service.contract_service import ContractService
from Service.achievement_service import AchievementService
from Service.product_service import ProductService
from Service.product_image_service import ProductImageService
from Service.skill_service import SkillService
from Service.target_service import TargetService

app = FastAPI(
    title="Profile API",
    description="API for Profile Management",
    version="1.0.0"
)

# Kiểm tra xem có đang chạy trên Vercel không
IS_VERCEL = os.getenv("VERCEL") == "1"

# Debug: Log env vars on Vercel (chỉ khi cần debug)
if IS_VERCEL:
    cloudinary_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloudinary_key = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_secret = os.getenv("CLOUDINARY_API_SECRET")
    print(f"[DEBUG] IS_VERCEL: {IS_VERCEL}")
    print(f"[DEBUG] CLOUDINARY_CLOUD_NAME: {'SET' if cloudinary_name else 'NOT SET'}")
    print(f"[DEBUG] CLOUDINARY_API_KEY: {'SET' if cloudinary_key else 'NOT SET'}")
    print(f"[DEBUG] CLOUDINARY_API_SECRET: {'SET' if cloudinary_secret else 'NOT SET'}")

# Kiểm tra xem có dùng Cloudinary không (nếu có env variables)
USE_CLOUDINARY = bool(
    os.getenv("CLOUDINARY_CLOUD_NAME") and 
    os.getenv("CLOUDINARY_API_KEY") and 
    os.getenv("CLOUDINARY_API_SECRET")
)

# Trên Vercel, bắt buộc phải dùng Cloudinary (không thể lưu file local)
if IS_VERCEL and not USE_CLOUDINARY:
    raise RuntimeError(
        "Cloudinary configuration required on Vercel. "
        "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables. "
        "Make sure to redeploy after setting environment variables."
    )

# Nếu không dùng Cloudinary và không phải Vercel, tạo thư mục uploads local (cho development)
if not USE_CLOUDINARY and not IS_VERCEL:
    UPLOAD_DIR = Path("uploads")
    UPLOAD_IMAGES_DIR = UPLOAD_DIR / "images"
    UPLOAD_PRODUCTS_DIR = UPLOAD_DIR / "products"
    try:
        UPLOAD_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        UPLOAD_PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
        # Mount static files để serve ảnh (chỉ khi không phải Vercel)
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    except Exception as e:
        print(f"Warning: Could not create upload directories or mount static files: {e}")
        print("Local file uploads will not be available. Please use Cloudinary instead.")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:3002",
        # "http://localhost:3000",
        # "http://localhost:5173",
        # "http://127.0.0.1:3002",
        # "http://127.0.0.1:3000",
        # "http://127.0.0.1:5173",
        # "https://*.vercel.app",  # Allow all Vercel preview deployments
        # # Thêm domain production frontend của bạn ở đây nếu có
        # # "https://your-frontend-domain.com",
        "https://duong-profile.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Profile API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/all")
async def all_():
    """Lấy tất cả dữ liệu từ bảng duong (test endpoint)"""
    try:
        client = connection.get_supabase_client()
        response = client.table("duong").select("*").execute()
        
        return {
            "data": response.data,
            "status": "success",
            "count": len(response.data) if response.data else 0
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


# ========== AUTH ROUTES ==========
@app.post("/login")
async def login(credentials: LoginRequest):
    """Đăng nhập với email và password"""
    return await AuthService.login(credentials)


@app.post("/register")
async def register(user_data: RegisterRequest):
    """Đăng ký tài khoản mới"""
    return await AuthService.register(user_data)


@app.get("/users/me")
async def get_current_user(token: str):
    """Lấy thông tin user hiện tại từ access token"""
    return await AuthService.get_current_user(token)


# ========== PROFILE ROUTES ==========
@app.post("/profile")
async def update_profile(profile_data: UpdateProfileRequest, token: str):
    """Cập nhật profile trong bảng duong"""
    return await ProfileService.update_profile(profile_data, token)


@app.get("/profile")
async def get_profile(token: str):
    """Lấy profile từ bảng duong"""
    return await ProfileService.get_profile(token)


@app.get("/profile/public")
async def get_public_profile():
    """Lấy profile public (không cần token) - lấy profile đầu tiên"""
    return await ProfileService.get_public_profile()


@app.get("/profile/public/all")
async def get_public_profile_all():
    """Lấy tất cả dữ liệu public (profile, images, educations, jobs, languages, contracts)"""
    try:
        # Lấy profile đầu tiên
        profile_res = await ProfileService.get_public_profile()
        
        if not profile_res or not profile_res.get("data"):
            return {
                "status": "success",
                "message": "No profile found",
                "profile": None,
                "images": {"data": []},
                "educations": {"data": []},
                "jobs": {"data": []},
                "languages": {"data": []},
                "contracts": {"data": []},
                "achievements": {"data": []},
                "products": {"data": []},
                "product_images": {"data": []}
            }
        
        user_id = profile_res["data"]["id"]
        
        # Lấy tất cả dữ liệu của user đó
        images = await ImageService.get_public_images(user_id)
        educations = await EducationService.get_public_educations(user_id)
        jobs = await JobService.get_public_jobs(user_id)
        languages = await LanguageService.get_public_languages(user_id)
        contracts = await ContractService.get_public_contracts(user_id)
        
        achievements = await AchievementService.get_public_achievements(user_id)
        products = await ProductService.get_public_products(user_id)
        product_images = await ProductImageService.get_public_product_images(user_id)
        skills = await SkillService.get_public_skills(user_id)
        targets = await TargetService.get_public_targets(user_id)

        return {
            "status": "success",
            "profile": profile_res,
            "images": images,
            "educations": educations,
            "jobs": jobs,
            "languages": languages,
            "contracts": contracts,
            "achievements": achievements,
            "products": products,
            "product_images": product_images,
            "skills": skills,
            "targets": targets
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get public profile all: {str(e)}")


# ========== UPLOAD ROUTES ==========
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...), token: str = None):
    """Upload ảnh và trả về đường dẫn"""
    try:
        # Kiểm tra token nếu có
        if token:
            from Service.base_service import get_user_and_client
            get_user_and_client(token)
        
        # Kiểm tra file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # Đọc nội dung file
        content = await file.read()
        
        # Upload lên Cloudinary hoặc lưu local
        if USE_CLOUDINARY:
            # Upload lên Cloudinary
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            public_id = f"images/{uuid.uuid4()}"
            
            result = await upload_image_to_cloudinary(
                file_content=content,
                folder="uploads/images",
                public_id=public_id
            )
            
            return {
                "status": "success",
                "message": "Upload thành công",
                "image_url": result["image_url"],
                "public_id": result["public_id"]
            }
        else:
            # Lưu local (development)
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_IMAGES_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Trả về đường dẫn (full URL)
            image_url = f"http://127.0.0.1:8000/uploads/images/{unique_filename}"
            return {
                "status": "success",
                "message": "Upload thành công",
                "image_url": image_url,
                "filename": unique_filename
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload thất bại: {str(e)}")


@app.post("/upload/product-image")
async def upload_product_image(file: UploadFile = File(...), token: str = None):
    """Upload ảnh sản phẩm và trả về đường dẫn"""
    try:
        # Kiểm tra token nếu có
        if token:
            from Service.base_service import get_user_and_client
            get_user_and_client(token)
        
        # Kiểm tra file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # Đọc nội dung file
        content = await file.read()
        
        # Upload lên Cloudinary hoặc lưu local
        if USE_CLOUDINARY:
            # Upload lên Cloudinary
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            public_id = f"products/{uuid.uuid4()}"
            
            result = await upload_image_to_cloudinary(
                file_content=content,
                folder="uploads/products",
                public_id=public_id
            )
            
            return {
                "status": "success",
                "message": "Upload thành công",
                "image_url": result["image_url"],
                "public_id": result["public_id"]
            }
        else:
            # Lưu local (development)
            file_ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_PRODUCTS_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Trả về đường dẫn (full URL)
            image_url = f"http://127.0.0.1:8000/uploads/products/{unique_filename}"
            return {
                "status": "success",
                "message": "Upload thành công",
                "image_url": image_url,
                "filename": unique_filename
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload thất bại: {str(e)}")


# ========== IMAGES ROUTES ==========
@app.post("/images")
async def create_image(data: CreateImageRequest, token: str):
    """Tạo image mới"""
    return await ImageService.create_image(data, token)


@app.get("/images")
async def get_images(token: str):
    """Lấy tất cả images của user"""
    return await ImageService.get_images(token)


@app.get("/images/{image_id}")
async def get_image(image_id: str, token: str):
    """Lấy image theo ID"""
    return await ImageService.get_image(image_id, token)


@app.put("/images/{image_id}")
async def update_image(image_id: str, data: UpdateImageRequest, token: str):
    """Cập nhật image"""
    return await ImageService.update_image(image_id, data, token)


@app.delete("/images/{image_id}")
async def delete_image(image_id: str, token: str):
    """Xóa image"""
    return await ImageService.delete_image(image_id, token)


# ========== EDUCATIONS ROUTES ==========
@app.post("/educations")
async def create_education(data: CreateEducationRequest, token: str):
    """Tạo education mới"""
    return await EducationService.create_education(data, token)


@app.get("/educations")
async def get_educations(token: str):
    """Lấy tất cả educations của user"""
    return await EducationService.get_educations(token)


@app.get("/educations/{education_id}")
async def get_education(education_id: str, token: str):
    """Lấy education theo ID"""
    return await EducationService.get_education(education_id, token)


@app.put("/educations/{education_id}")
async def update_education(education_id: str, data: UpdateEducationRequest, token: str):
    """Cập nhật education"""
    return await EducationService.update_education(education_id, data, token)


@app.delete("/educations/{education_id}")
async def delete_education(education_id: str, token: str):
    """Xóa education"""
    return await EducationService.delete_education(education_id, token)


# ========== JOBS ROUTES ==========
@app.post("/jobs")
async def create_job(data: CreateJobRequest, token: str):
    """Tạo job mới"""
    return await JobService.create_job(data, token)


@app.get("/jobs")
async def get_jobs(token: str):
    """Lấy tất cả jobs của user"""
    return await JobService.get_jobs(token)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str, token: str):
    """Lấy job theo ID"""
    return await JobService.get_job(job_id, token)


@app.put("/jobs/{job_id}")
async def update_job(job_id: str, data: UpdateJobRequest, token: str):
    """Cập nhật job"""
    return await JobService.update_job(job_id, data, token)


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, token: str):
    """Xóa job"""
    return await JobService.delete_job(job_id, token)


# ========== LANGUAGES ROUTES ==========
@app.post("/languages")
async def create_language(data: CreateLanguageRequest, token: str):
    """Tạo language mới"""
    return await LanguageService.create_language(data, token)


@app.get("/languages")
async def get_languages(token: str):
    """Lấy tất cả languages của user"""
    return await LanguageService.get_languages(token)


@app.get("/languages/{language_id}")
async def get_language(language_id: str, token: str):
    """Lấy language theo ID"""
    return await LanguageService.get_language(language_id, token)


@app.put("/languages/{language_id}")
async def update_language(language_id: str, data: UpdateLanguageRequest, token: str):
    """Cập nhật language"""
    return await LanguageService.update_language(language_id, data, token)


@app.delete("/languages/{language_id}")
async def delete_language(language_id: str, token: str):
    """Xóa language"""
    return await LanguageService.delete_language(language_id, token)


# ========== CONTRACTS ROUTES ==========
@app.post("/contracts")
async def create_contract(data: CreateContractRequest, token: str):
    """Tạo contract mới"""
    return await ContractService.create_contract(data, token)


@app.get("/contracts")
async def get_contracts(token: str):
    """Lấy tất cả contracts của user"""
    return await ContractService.get_contracts(token)


@app.get("/contracts/{contract_id}")
async def get_contract(contract_id: str, token: str):
    """Lấy contract theo ID"""
    return await ContractService.get_contract(contract_id, token)


@app.put("/contracts/{contract_id}")
async def update_contract(contract_id: str, data: UpdateContractRequest, token: str):
    """Cập nhật contract"""
    return await ContractService.update_contract(contract_id, data, token)


@app.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str, token: str):
    """Xóa contract"""
    return await ContractService.delete_contract(contract_id, token)


# ========== ACHIEVEMENTS ROUTES ==========
@app.post("/achievements")
async def create_achievement(data: CreateAchievementRequest, token: str):
    """Tạo achievement mới"""
    return await AchievementService.create_achievement(data, token)


@app.get("/achievements")
async def get_achievements(token: str):
    """Lấy tất cả achievements của user"""
    return await AchievementService.get_achievements(token)


@app.get("/achievements/{achievement_id}")
async def get_achievement(achievement_id: str, token: str):
    """Lấy achievement theo ID"""
    return await AchievementService.get_achievement(achievement_id, token)


@app.put("/achievements/{achievement_id}")
async def update_achievement(achievement_id: str, data: UpdateAchievementRequest, token: str):
    """Cập nhật achievement"""
    return await AchievementService.update_achievement(achievement_id, data, token)


@app.delete("/achievements/{achievement_id}")
async def delete_achievement(achievement_id: str, token: str):
    """Xóa achievement"""
    return await AchievementService.delete_achievement(achievement_id, token)


# ========== PRODUCTS ROUTES ==========
@app.post("/products")
async def create_product(data: CreateProductRequest, token: str):
    """Tạo product mới"""
    return await ProductService.create_product(data, token)


@app.get("/products")
async def get_products(token: str):
    """Lấy tất cả products của user"""
    return await ProductService.get_products(token)


@app.get("/products/{product_id}")
async def get_product(product_id: str, token: str):
    """Lấy product theo ID"""
    return await ProductService.get_product(product_id, token)


@app.put("/products/{product_id}")
async def update_product(product_id: str, data: UpdateProductRequest, token: str):
    """Cập nhật product"""
    return await ProductService.update_product(product_id, data, token)


@app.delete("/products/{product_id}")
async def delete_product(product_id: str, token: str):
    """Xóa product"""
    return await ProductService.delete_product(product_id, token)


# ========== PRODUCT IMAGES ROUTES ==========
@app.post("/product-images")
async def create_product_image(data: CreateProductImageRequest, token: str):
    """Tạo product image mới"""
    return await ProductImageService.create_product_image(data, token)


@app.get("/product-images")
async def get_product_images(token: str, product_id: str = None):
    """Lấy tất cả product images của user, hoặc của một product cụ thể"""
    return await ProductImageService.get_product_images(token, product_id)


@app.get("/product-images/{image_id}")
async def get_product_image(image_id: str, token: str):
    """Lấy product image theo ID"""
    return await ProductImageService.get_product_image(image_id, token)


@app.put("/product-images/{image_id}")
async def update_product_image(image_id: str, data: UpdateProductImageRequest, token: str):
    """Cập nhật product image"""
    return await ProductImageService.update_product_image(image_id, data, token)


@app.delete("/product-images/{image_id}")
async def delete_product_image(image_id: str, token: str):
    """Xóa product image"""
    return await ProductImageService.delete_product_image(image_id, token)


# ========== SKILLS ROUTES ==========
@app.post("/skills")
async def create_skill(data: CreateSkillRequest, token: str):
    """Tạo skill mới"""
    return await SkillService.create_skill(data, token)


@app.get("/skills")
async def get_skills(token: str):
    """Lấy tất cả skills của user"""
    return await SkillService.get_skills(token)


@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str, token: str):
    """Lấy skill theo ID"""
    return await SkillService.get_skill(skill_id, token)


@app.put("/skills/{skill_id}")
async def update_skill(skill_id: str, data: UpdateSkillRequest, token: str):
    """Cập nhật skill"""
    return await SkillService.update_skill(skill_id, data, token)


@app.delete("/skills/{skill_id}")
async def delete_skill(skill_id: str, token: str):
    """Xóa skill"""
    return await SkillService.delete_skill(skill_id, token)


# ========== TARGETS ROUTES ==========
@app.post("/targets")
async def create_target(data: CreateTargetRequest, token: str):
    """Tạo target mới"""
    return await TargetService.create_target(data, token)


@app.get("/targets")
async def get_targets(token: str):
    """Lấy tất cả targets của user"""
    return await TargetService.get_targets(token)


@app.get("/targets/{target_id}")
async def get_target(target_id: str, token: str):
    """Lấy target theo ID"""
    return await TargetService.get_target(target_id, token)


@app.put("/targets/{target_id}")
async def update_target(target_id: str, data: UpdateTargetRequest, token: str):
    """Cập nhật target"""
    return await TargetService.update_target(target_id, data, token)


@app.delete("/targets/{target_id}")
async def delete_target(target_id: str, token: str):
    """Xóa target"""
    return await TargetService.delete_target(target_id, token)
