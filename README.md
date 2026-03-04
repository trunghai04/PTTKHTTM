# Text Classification System (PTHTTM)

Hệ thống phân loại văn bản thông minh với AI, bao gồm:

- 📧 **Spam Detection**: Phát hiện email spam (nhập tay hoặc quét Gmail)
- 📰 **News Classification**: Phân loại tin tức theo 5 chủ đề (Thể thao, Chính trị, Kinh tế, Công nghệ, Giải trí)
- 📊 **Statistics Dashboard**: Thống kê và phân tích dữ liệu (yêu cầu đăng nhập)
- 🔐 **Xác thực**: Đăng ký/đăng nhập email + Đăng nhập với Google
- 📬 **Gmail Scan**: Quét hộp thư Gmail bằng mô hình spam (sau khi đăng nhập Google)

## 🏗️ Kiến trúc hệ thống

```
Frontend (React + Vite) → Backend (FastAPI) → PostgreSQL
                                    ↓
                          ML Models (TF-IDF + Logistic Regression)
                                    ↓
                          Google OAuth / Gmail API (tùy chọn)
```

## 📁 Cấu trúc dự án

```
PTHTTM/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── auth/           # Bảo mật, JWT, Google OAuth
│   │   ├── routes/         # spam, news, stats, auth, gmail
│   │   ├── services/       # spam_service, news_service
│   │   ├── database/       # models, db
│   │   └── ...
│   ├── train_model.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Navbar, ProtectedRoute
│   │   ├── pages/          # Home, SpamPage, NewsPage, Login, Dashboard, ScanHistory, ...
│   │   ├── api/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── DOCS.md                 # Tài liệu chi tiết API & luồng
```

## 🚀 Cài đặt và chạy

### Sử dụng Docker (Khuyến nghị)

1. **Clone và vào thư mục dự án**

2. **(Tùy chọn)** Tạo file `.env` ở thư mục gốc nếu dùng Google Login / Gmail:
   ```env
   GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=xxx
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   FRONTEND_URL=http://localhost:3000
   ```

3. **Chạy toàn bộ hệ thống:**
   ```bash
   docker-compose up --build
   ```

4. **Truy cập:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Cài đặt thủ công

#### Database (PostgreSQL)

Chạy PostgreSQL và tạo database `text_classification`, hoặc dùng SQLite (sửa `DATABASE_URL` trong backend).

#### Backend

```bash
cd backend
cp .env.example .env   # Chỉnh sửa nếu cần
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

Cấu hình `VITE_API_URL` trỏ tới backend (mặc định http://localhost:8000).

## ⚙️ Biến môi trường

| Biến | Mô tả | Bắt buộc |
|------|--------|----------|
| `DATABASE_URL` | Kết nối PostgreSQL (hoặc SQLite) | Khuyến nghị |
| `JWT_SECRET` | Secret cho JWT (đổi trong production) | Tùy chọn |
| `JWT_EXPIRES_MINUTES` | Thời hạn token (mặc định 1440) | Tùy chọn |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Cho Login Google & Gmail |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Cho Login Google & Gmail |
| `GOOGLE_REDIRECT_URI` | Callback URL backend (vd: `http://localhost:8000/api/auth/google/callback`) | Cho Google |
| `FRONTEND_URL` | URL frontend (vd: `http://localhost:3000`) | Cho redirect sau login |

Chi tiết xem `backend/.env.example`.

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

### Spam
- `POST /api/spam/predict` — Dự đoán spam (body: `{ "text": "..." }`)
- `POST /api/spam/predict/bulk` — Dự đoán nhiều văn bản
- `GET /api/spam/history` — Lịch sử dự đoán spam

### News
- `POST /api/news/predict` — Phân loại tin tức
- `POST /api/news/predict/bulk` — Phân loại hàng loạt
- `GET /api/news/history` — Lịch sử dự đoán tin tức

### Statistics
- `GET /api/stats/overview` — Tổng quan thống kê
- `GET /api/stats/news/categories` — Thống kê theo chủ đề

### Auth
- `POST /api/auth/register` — Đăng ký (email + password)
- `POST /api/auth/login` — Đăng nhập (email + password)
- `GET /api/auth/me` — Thông tin user (header: `Authorization: Bearer <token>`)
- `GET /api/auth/google/login` — Lấy URL đăng nhập Google
- `GET /api/auth/google/callback` — Callback OAuth (redirect từ Google)

### Gmail (yêu cầu đăng nhập, Bearer token)
- `POST /api/gmail/scan` — Quét hộp thư Gmail, chạy spam classifier, lưu vào lịch sử
- `GET /api/gmail/history` — Lịch sử kết quả quét Gmail của user

## 🗄️ Database Schema

### Bảng: users
| Column | Type | Mô tả |
|--------|------|--------|
| id | Integer | Primary key |
| email | String | Unique |
| name | String | Nullable |
| hashed_password | String | Null cho user chỉ dùng Google |
| google_id | String | Unique, nullable |
| google_refresh_token | String | Nullable, dùng cho Gmail API |
| created_at | DateTime | |

### Bảng: predictions
| Column | Type | Mô tả |
|--------|------|--------|
| id | Integer | Primary key |
| text | String | Nội dung văn bản |
| type | Enum | `spam` hoặc `news` |
| predicted_label | String | Nhãn dự đoán |
| confidence | Float | Độ tin cậy (0–1) |
| created_at | DateTime | |
| user_id | Integer | Nullable, FK users |
| source | String | `gmail` \| `manual` \| null |
| email_subject | String | Nullable |
| email_snippet | String | Nullable |

## 📊 Tính năng

- ✅ Phân loại email spam (nhập tay / bulk)
- ✅ Phân loại tin tức 5 chủ đề
- ✅ Lưu lịch sử dự đoán (có thể gắn user_id)
- ✅ Dashboard thống kê (cần đăng nhập)
- ✅ Lịch sử quét (Scan History) theo user
- ✅ Đăng ký / Đăng nhập email + Đăng nhập với Google
- ✅ Quét Gmail bằng mô hình spam (sau khi liên kết Google)
- ✅ Hiển thị độ tin cậy, cảnh báo confidence thấp
- ✅ Responsive design

## 🛠️ Công nghệ

- **Backend**: FastAPI, SQLAlchemy, scikit-learn, python-jose, google-auth-oauthlib, google-api-python-client
- **Frontend**: React, Vite, React Router, Recharts, Framer Motion, TailwindCSS, Axios
- **Database**: PostgreSQL
- **ML**: TF-IDF, Logistic Regression
- **Deployment**: Docker, Docker Compose

## 📝 Ghi chú

- Mô hình được train khi chạy `train_model.py` (hoặc khi khởi động backend trong Docker).
- Cải thiện độ chính xác: dùng dataset lớn hơn hoặc dữ liệu thực tế.
- Google Login & Gmail: cấu hình OAuth tại [Google Cloud Console](https://console.cloud.google.com/apis/credentials), bật Gmail API nếu dùng quét Gmail.

## 📄 Tài liệu thêm

- [DOCS.md](./DOCS.md) — Tài liệu chi tiết API, luồng đăng nhập, Gmail, và hướng dẫn triển khai.

## 📄 License

MIT License
