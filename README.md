# Text Classification System

Hệ thống phân loại văn bản thông minh với AI, bao gồm:
- 📧 **Spam Detection**: Phát hiện email spam
- 📰 **News Classification**: Phân loại tin tức theo 5 chủ đề (Thể thao, Chính trị, Kinh tế, Công nghệ, Giải trí)
- 📊 **Statistics Dashboard**: Thống kê và phân tích dữ liệu

## 🏗️ Kiến trúc hệ thống

```
Frontend (React) → Backend (FastAPI) → PostgreSQL
                         ↓
                   ML Models (TF-IDF + Logistic Regression)
```

## 📁 Cấu trúc dự án

```
PTHTTM/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── database/
│   │   └── utils/
│   ├── train_model.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## 🚀 Cài đặt và chạy

### Sử dụng Docker (Khuyến nghị)

1. **Clone repository và di chuyển vào thư mục dự án**

2. **Chạy toàn bộ hệ thống:**
```bash
docker-compose up --build
```

3. **Truy cập:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Cài đặt thủ công

#### Backend

```bash
cd backend
pip install -r requirements.txt
python train_model.py
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Database

Cần có PostgreSQL đang chạy và cấu hình `DATABASE_URL` trong `.env`

## 🧠 Mô hình AI

### Spam Classification
- **Vectorization**: TF-IDF
- **Model**: Logistic Regression
- **Labels**: Spam / Not Spam

### News Classification
- **Vectorization**: TF-IDF
- **Model**: Logistic Regression
- **Labels**: Thể thao, Chính trị, Kinh tế, Công nghệ, Giải trí

## 📡 API Endpoints

### Spam API
- `POST /api/spam/predict` - Dự đoán spam
- `GET /api/spam/history` - Lịch sử dự đoán spam

### News API
- `POST /api/news/predict` - Phân loại tin tức
- `GET /api/news/history` - Lịch sử dự đoán tin tức

### Statistics API
- `GET /api/stats/overview` - Tổng quan thống kê
- `GET /api/stats/news/categories` - Thống kê theo chủ đề

## 🗄️ Database Schema

### Bảng: predictions
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| text | String | Nội dung văn bản |
| type | Enum | spam hoặc news |
| predicted_label | String | Nhãn dự đoán |
| confidence | Float | Độ tin cậy (0-1) |
| created_at | DateTime | Thời gian tạo |

## 📊 Tính năng

- ✅ Phân loại email spam
- ✅ Phân loại tin tức 5 chủ đề
- ✅ Lưu lịch sử dự đoán
- ✅ Dashboard thống kê với biểu đồ
- ✅ Hiển thị độ tin cậy
- ✅ Responsive design

## 🛠️ Công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy, scikit-learn
- **Frontend**: React, Vite, Recharts
- **Database**: PostgreSQL
- **ML**: TF-IDF, Logistic Regression
- **Deployment**: Docker, Docker Compose

## 📝 Ghi chú

- Models được train tự động khi khởi động backend lần đầu
- Có thể cải thiện độ chính xác bằng cách sử dụng dataset lớn hơn
- Để production, nên sử dụng dataset thực tế cho training

## 📄 License

MIT License
