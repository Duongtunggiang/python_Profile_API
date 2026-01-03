# Hướng dẫn Deploy FastAPI lên Vercel

## Cấu trúc thư mục
```
Creative/
├── api/
│   └── index.py          # Entry point cho Vercel
├── main.py               # FastAPI app chính
├── vercel.json           # Cấu hình Vercel
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables (không commit)
```

## Các bước deploy

1. **Đảm bảo có file `api/index.py`** với nội dung:
   ```python
   from main import app
   handler = app
   ```

2. **Cấu hình `vercel.json`** đã đúng

3. **Thêm Environment Variables trong Vercel Dashboard:**
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `CLOUDINARY_CLOUD_NAME` (nếu dùng Cloudinary)
   - `CLOUDINARY_API_KEY` (nếu dùng Cloudinary)
   - `CLOUDINARY_API_SECRET` (nếu dùng Cloudinary)

4. **Deploy:**
   ```bash
   vercel
   ```

## Lưu ý

- Vercel sẽ tự động install dependencies từ `requirements.txt`
- Environment variables phải được set trong Vercel Dashboard
- File uploads sẽ không persist trên Vercel (dùng Cloudinary thay thế)
- Static files từ `uploads/` sẽ không hoạt động trên Vercel

## Troubleshooting

Nếu gặp lỗi "Not Found":
1. Kiểm tra `api/index.py` có export `handler = app`
2. Kiểm tra `vercel.json` có đúng cấu hình
3. Kiểm tra environment variables đã được set
4. Kiểm tra logs trong Vercel Dashboard

