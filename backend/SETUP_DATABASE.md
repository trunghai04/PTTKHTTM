# 🗄️ Hướng dẫn Setup Database

## 🎯 Mục đích

Database dùng để **lưu lịch sử predictions**:
- 📝 Lưu lại mọi prediction đã thực hiện
- 📊 Hiển thị thống kê trong Dashboard
- 🔍 Xem lại lịch sử predictions

## ✅ Option 1: SQLite (Khuyến nghị - Đơn giản nhất)

**Ưu điểm:**
- ✅ Không cần cài đặt gì
- ✅ Tự động tạo file database
- ✅ Hoạt động ngay lập tức

**Cách dùng:**
1. Không cần làm gì cả! Hệ thống tự động dùng SQLite
2. File database sẽ được tạo tại: `backend/database.db`
3. Chạy backend bình thường:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

**Lưu ý:** SQLite phù hợp cho development và demo. Cho production nên dùng PostgreSQL.

---

## 🐘 Option 2: PostgreSQL (Cho production)

### Cách 1: Dùng Docker (Dễ nhất)

```bash
# Chạy PostgreSQL trong Docker
docker run -d \
  --name postgres_text_classification \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=text_classification \
  -p 5432:5432 \
  postgres:15-alpine
```

Sau đó set environment variable:
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/text_classification"

# Windows CMD
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/text_classification

# Linux/Mac
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/text_classification"
```

### Cách 2: Cài PostgreSQL thủ công

1. **Cài PostgreSQL:**
   - Windows: Download từ https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. **Tạo database:**
   ```sql
   CREATE DATABASE text_classification;
   ```

3. **Set environment variable:**
   ```bash
   set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/text_classification
   ```

4. **Cài Python package:**
   ```bash
   pip install psycopg2-binary
   ```

---

## 🚀 Chạy Backend với Database

```bash
cd backend
uvicorn app.main:app --reload
```

Backend sẽ:
- ✅ Tự động tạo tables nếu chưa có
- ✅ Lưu mọi prediction vào database
- ✅ API `/api/stats/overview` sẽ có dữ liệu

---

## 🧪 Test Database

### 1. Test Prediction (sẽ tự động lưu vào DB)
```bash
curl -X POST http://localhost:8000/api/spam/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"You won a free iPhone!\"}"
```

### 2. Xem lịch sử
```bash
curl http://localhost:8000/api/spam/history
```

### 3. Xem thống kê
```bash
curl http://localhost:8000/api/stats/overview
```

---

## 📊 Kiểm tra Database

### SQLite
```bash
# Xem file database
ls backend/database.db

# Hoặc dùng SQLite browser
# Download: https://sqlitebrowser.org/
```

### PostgreSQL
```bash
# Kết nối vào database
psql -U postgres -d text_classification

# Xem tables
\dt

# Xem dữ liệu
SELECT * FROM predictions LIMIT 10;
```

---

## 🔧 Troubleshooting

### Lỗi: "Could not create database tables"
- **SQLite:** Kiểm tra quyền ghi file trong thư mục `backend/`
- **PostgreSQL:** Kiểm tra kết nối và credentials

### Lỗi: "Connection timeout"
- Kiểm tra PostgreSQL có đang chạy không
- Kiểm tra port 5432 có bị block không
- Thử dùng SQLite thay thế

### Lỗi: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

---

## ✅ Tóm tắt

| Database | Cài đặt | Phù hợp cho |
|----------|---------|-------------|
| **SQLite** | Không cần | Development, Demo |
| **PostgreSQL** | Cần cài | Production |

**Khuyến nghị:** Dùng SQLite cho development, PostgreSQL cho production.
