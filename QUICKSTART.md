# 🚀 Hướng dẫn nhanh

## Cài đặt và chạy với Docker

### Bước 1: Đảm bảo đã cài Docker và Docker Compose

```bash
docker --version
docker-compose --version
```

### Bước 2: Chạy hệ thống

```bash
docker-compose up --build
```

Lần đầu chạy sẽ mất vài phút để:
- Tải images
- Cài đặt dependencies
- Train ML models
- Khởi động services

### Bước 3: Truy cập ứng dụng

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## Cài đặt thủ công (không dùng Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

Cần có PostgreSQL đang chạy và tạo database:

```sql
CREATE DATABASE text_classification;
```

Cấu hình `DATABASE_URL` trong file `.env` của backend.

## Kiểm tra hệ thống

1. Mở http://localhost:3000
2. Thử phân loại spam: Nhập "You won a free iPhone!"
3. Thử phân loại tin tức: Nhập "Messi ghi bàn trong trận chung kết"
4. Xem Dashboard: Click vào "Dashboard" để xem thống kê

## Troubleshooting

### Lỗi kết nối database
- Đảm bảo PostgreSQL đang chạy
- Kiểm tra `DATABASE_URL` trong `.env`

### Models chưa được train
- Chạy `python backend/train_model.py` thủ công
- Hoặc đợi Docker tự động train khi khởi động

### Port đã được sử dụng
- Đổi port trong `docker-compose.yml` hoặc
- Dừng service đang dùng port đó

## Dừng hệ thống

```bash
docker-compose down
```

Để xóa cả database:

```bash
docker-compose down -v
```
