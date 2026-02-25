# 🚀 Chạy hệ thống KHÔNG CẦN DATABASE

## ✅ Quan trọng

**Models KHÔNG cần database để hoạt động!**

- ✅ Models (`.pkl` files) hoạt động độc lập
- ✅ Database chỉ để **lưu lịch sử** predictions
- ✅ Nếu không có database, API vẫn hoạt động bình thường

## 📦 Models đã được train

Models đã có sẵn tại:
- `backend/app/models/spam_model.pkl`
- `backend/app/models/spam_vectorizer.pkl`
- `backend/app/models/news_model.pkl`
- `backend/app/models/news_vectorizer.pkl`

## 🚀 Chạy Backend (không cần database)

```bash
cd backend
uvicorn app.main:app --reload
```

Backend sẽ:
- ✅ Load models tự động
- ✅ API hoạt động bình thường
- ⚠️  Không lưu lịch sử (nếu không có DB)

## 🧪 Test API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Spam Prediction
```bash
curl -X POST http://localhost:8000/api/spam/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"You won a free iPhone!\"}"
```

### 3. Test News Prediction
```bash
curl -X POST http://localhost:8000/api/news/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Messi ghi bàn trong trận chung kết\"}"
```

## 📊 Khi nào cần Database?

Database chỉ cần khi bạn muốn:
- 📝 Lưu lịch sử predictions
- 📈 Xem thống kê trong Dashboard
- 🔍 Xem lại các predictions trước đó

## 🔧 Nếu muốn dùng Database

### Option 1: Dùng Docker (dễ nhất)
```bash
docker-compose up
```

### Option 2: Cài PostgreSQL thủ công
1. Cài PostgreSQL
2. Tạo database: `CREATE DATABASE text_classification;`
3. Set environment variable:
   ```bash
   set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/text_classification
   ```

## ✅ Tóm tắt

| Tính năng | Cần Database? |
|-----------|---------------|
| Spam Prediction | ❌ Không |
| News Prediction | ❌ Không |
| Lưu lịch sử | ✅ Có |
| Dashboard stats | ✅ Có |

**Kết luận:** Bạn có thể chạy và test API ngay mà không cần database!
