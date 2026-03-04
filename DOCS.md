# Tài liệu chi tiết — Text Classification System (PTHTTM)

Tài liệu này mô tả API, luồng xác thực, tích hợp Gmail và hướng dẫn triển khai.

---

## 1. Tổng quan luồng người dùng

### 1.1 Không cần đăng nhập
- **Trang chủ**: Giới thiệu, điều hướng.
- **Spam**: Nhập văn bản → gọi `POST /api/spam/predict` → xem kết quả + độ tin cậy. Lịch sử lưu không gắn user.
- **News**: Nhập văn bản → gọi `POST /api/news/predict` → xem chủ đề. Lịch sử tương tự.

### 1.2 Cần đăng nhập
- **Dashboard**: Thống kê tổng quan (có thể mở rộng theo user).
- **Scan History**: Lịch sử dự đoán / quét Gmail của user (Bearer token).
- **Gmail Scan**: Chỉ dùng được sau khi đăng nhập bằng Google; quét hộp thư và lưu kết quả spam vào lịch sử.

### 1.3 Đăng nhập
- **Email/Password**: `POST /api/auth/register` và `POST /api/auth/login` → nhận JWT, lưu (localStorage/sessionStorage) → gửi header `Authorization: Bearer <token>` cho API bảo vệ.
- **Google**: Frontend gọi `GET /api/auth/google/login` → redirect user tới Google → sau khi đồng ý, Google redirect về `GET /api/auth/google/callback` (backend) → backend đổi code lấy token, tạo/cập nhật user, redirect về frontend kèm JWT trong query: `FRONTEND_URL/auth/google/callback?token=...`. Frontend lưu token và chuyển vào app.

---

## 2. API chi tiết

Base URL mặc định: `http://localhost:8000`

### 2.1 Spam

| Method | Endpoint | Mô tả | Auth |
|--------|----------|--------|------|
| POST | `/api/spam/predict` | Dự đoán 1 văn bản | Không |
| POST | `/api/spam/predict/bulk` | Dự đoán nhiều văn bản | Không |
| GET | `/api/spam/history` | Lịch sử dự đoán spam | Không |

**Ví dụ `POST /api/spam/predict`:**
```json
// Request
{ "text": "Nội dung email hoặc tin nhắn cần kiểm tra" }

// Response
{
  "label": "Spam",
  "confidence": 0.92,
  "spam_probability": 0.92,
  "not_spam_probability": 0.08,
  "id": 123,
  "warning": null
}
```
Nếu `confidence < 0.7` có thể có trường `warning` gợi ý model cần thêm dữ liệu.

### 2.2 News

| Method | Endpoint | Mô tả | Auth |
|--------|----------|--------|------|
| POST | `/api/news/predict` | Phân loại 1 tin | Không |
| POST | `/api/news/predict/bulk` | Phân loại nhiều tin | Không |
| GET | `/api/news/history` | Lịch sử dự đoán tin tức | Không |

**Ví dụ `POST /api/news/predict`:**
```json
// Request
{ "text": "Nội dung tin tức" }

// Response
{ "label": "Công nghệ", "confidence": 0.88, "id": 456 }
```

### 2.3 Statistics

| Method | Endpoint | Mô tả | Auth |
|--------|----------|--------|------|
| GET | `/api/stats/overview` | Tổng quan thống kê | Không |
| GET | `/api/stats/news/categories` | Thống kê theo chủ đề tin | Không |

### 2.4 Auth

| Method | Endpoint | Mô tả | Auth |
|--------|----------|--------|------|
| POST | `/api/auth/register` | Đăng ký | Không |
| POST | `/api/auth/login` | Đăng nhập | Không |
| GET | `/api/auth/me` | Thông tin user hiện tại | Bearer |
| GET | `/api/auth/google/login` | Lấy URL đăng nhập Google | Không |
| GET | `/api/auth/google/callback` | Callback OAuth (backend) | Không (Google redirect) |

**Register:**
```json
// POST /api/auth/register
{ "email": "user@example.com", "password": "secret123", "name": "Tên" }
// Password tối thiểu 6 ký tự.

// Response
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "user@example.com", "name": "Tên" }
}
```

**Login:**
```json
// POST /api/auth/login
{ "email": "user@example.com", "password": "secret123" }
// Response cùng format như register.
```

**Me (cần header):**
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```
Response: `{ "id": 1, "email": "...", "name": "..." }`

**Google Login (luồng):**
1. Frontend: `GET /api/auth/google/login` → nhận `{ "url": "https://accounts.google.com/...", "state": "..." }`.
2. Redirect user tới `url`.
3. User đăng nhập Google và đồng ý scope.
4. Google redirect về `GOOGLE_REDIRECT_URI` (backend) với `?code=...&state=...`.
5. Backend đổi code lấy token, tạo/cập nhật user, redirect tới `FRONTEND_URL/auth/google/callback?token=<JWT>`.
6. Frontend đọc `token` từ query, lưu và chuyển vào app (Dashboard / Scan History).

### 2.5 Gmail (yêu cầu Bearer token + đã đăng nhập Google)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|--------|------|
| POST | `/api/gmail/scan` | Quét hộp thư, chạy spam classifier, lưu vào predictions | Bearer |
| GET | `/api/gmail/history` | Lịch sử kết quả quét Gmail của user | Bearer |

**Scan:**
```http
POST /api/gmail/scan?max_messages=50
Authorization: Bearer <access_token>
```
- User phải có `google_refresh_token` (đã đăng nhập Google ít nhất một lần).
- Backend dùng Gmail API lấy danh sách email, trích nội dung (subject + body/snippet), gọi spam classifier, lưu từng kết quả vào bảng `predictions` với `source='gmail'`, `user_id` = user hiện tại.
- Response: `{ "scanned": 50, "spam_count": 5, "not_spam_count": 45 }`.

**History:**
```http
GET /api/gmail/history?limit=50
Authorization: Bearer <access_token>
```
Trả về danh sách predictions có `type=spam`, `source=gmail`, `user_id` = user hiện tại.

---

## 3. Cấu hình Google OAuth & Gmail

1. Vào [Google Cloud Console](https://console.cloud.google.com/) → tạo project (hoặc chọn project có sẵn).
2. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**.
3. Loại: **Web application**.
4. **Authorized redirect URIs**: thêm đúng URL backend callback, ví dụ:
   - Local: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://your-api-domain.com/api/auth/google/callback`
5. Lấy **Client ID** và **Client Secret** → gán vào `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` trong `.env` hoặc docker-compose.
6. Nếu dùng **Gmail Scan**: **APIs & Services** → **Library** → bật **Gmail API**.
7. **FRONTEND_URL**: URL giao diện (vd: `http://localhost:3000` hoặc `https://your-frontend.com`) để backend redirect sau khi Google login thành công.

---

## 4. Frontend — Routes & bảo vệ

| Route | Trang | Bảo vệ |
|-------|--------|--------|
| `/` | Home | Không |
| `/spam` | SpamPage | Không |
| `/news` | NewsPage | Không |
| `/login` | Login | Không |
| `/auth/google/callback` | GoogleAuthCallback (xử lý token từ query) | Không |
| `/dashboard` | Dashboard | Có (ProtectedRoute) |
| `/scan-history` | ScanHistory | Có (ProtectedRoute) |

**ProtectedRoute**: Nếu chưa có token (vd trong localStorage), redirect về `/login`. Có token thì render children (Dashboard / ScanHistory).

---

## 5. Database & Migration

- **ORM**: SQLAlchemy. Bảng: `users`, `predictions`.
- Khi chạy `app.main`, backend tự tạo bảng nếu chưa có (`Base.metadata.create_all`) và chạy migration thêm cột (vd: `user_id`, `source`, `email_subject`, `email_snippet`) nếu thiếu. Cột đã tồn tại thì bỏ qua.

Nếu dùng PostgreSQL production, nên backup và có kế hoạch migration chính thức (vd Alembic) khi schema thay đổi phức tạp.

---

## 6. Triển khai (Production) — Gợi ý

- **Backend**: Chạy qua Gunicorn + Uvicorn worker, phía sau reverse proxy (Nginx/Caddy). Đặt `JWT_SECRET` mạnh, `JWT_EXPIRES_MINUTES` hợp lý.
- **Frontend**: Build `npm run build`, serve static qua Nginx hoặc CDN. Cấu hình `VITE_API_URL` trỏ tới URL API thật.
- **CORS**: Trong `main.py` hiện cho phép `localhost:3000`, `localhost:5173`. Production cần thêm origin frontend thật vào `allow_origins`.
- **Google**: Redirect URI trong Console phải khớp đúng với URL backend (http/https, domain, path). `FRONTEND_URL` cũng phải đúng để redirect sau login không lỗi.
- **Database**: Dùng PostgreSQL, bảo mật kết nối (strong password, firewall). Có thể dùng connection pooling (vd PgBouncer) nếu cần.

---

## 7. Tài liệu tham khảo nhanh

- API tương tác: http://localhost:8000/docs (Swagger UI).
- Backend health: `GET /health` → `{ "status": "healthy" }`.
- Root: `GET /` → `{ "message": "Text Classification API", "version": "1.0.0" }`.
Nếu cần mở rộng API (vd filter history theo ngày, export CSV, hoặc thêm role admin), có thể mở rộng từ các route và model hiện có trong `backend/app/`.

---

## 8. Mô hình, huấn luyện và công thức tính toán

### 8.1 Dữ liệu và tiền xử lý

- **Nguồn dữ liệu**: file Excel `backend/dataset.xlsx` với các cột:
  - `Nội Dung`: văn bản gốc (email / tin tức).
  - `Nhãn/Label`: nhãn lớp.
  - (Cột `STT` chỉ để đánh số, không dùng huấn luyện).
- **Phân loại Spam**:
  - Lọc các dòng có nhãn thuộc tập `["Spam", "Not Spam"]`.
  - Map nhãn: `"Not Spam" → 0`, `"Spam" → 1`.
- **Phân loại News**:
  - Lấy toàn bộ các dòng *không* thuộc 2 nhãn spam ở trên.
  - Nhãn được suy ra động từ dữ liệu (ví dụ: `Thể thao`, `Chính trị`, `Kinh tế`, `Công nghệ`, `Giải trí`, ...).
- **Làm sạch văn bản**:
  - Dùng hàm `clean_text` trong `app.utils.preprocess` cho cả spam và news:
    - Chuẩn hóa chuỗi, lower-case.
    - Loại bỏ ký tự đặc biệt, khoảng trắng thừa.
    - (Có thể mở rộng thêm bước chuẩn hóa dấu, số, v.v.).
- **Cân bằng dữ liệu (class balancing)**:
  - Hàm `balance_data` trong `train_model.py`:
    - Tính số mẫu mỗi lớp.
    - Chọn `min_samples_per_class` (mặc định = số mẫu lớn nhất).
    - Với từng lớp:
      - Nếu ít hơn `min_samples_per_class` → **upsample** (lấy mẫu lại có hoàn lại).
      - Nếu nhiều hơn → **downsample**.
    - Gộp lại và shuffle toàn bộ tập.

### 8.2 Biểu diễn TF–IDF

Sau khi tiền xử lý, văn bản được đưa qua **TfidfVectorizer** để chuyển thành vector.

- **Term Frequency (TF)** của từ \(t\) trong văn bản \(d\):

\[
tf_{t,d} = \frac{f_{t,d}}{\sum_k f_{k,d}}
\]

trong đó \(f_{t,d}\) là số lần xuất hiện của từ \(t\) trong văn bản \(d\).

- **Inverse Document Frequency (IDF)**:

\[
idf_t = \log\left(\frac{N}{df_t + 1}\right)
\]

trong đó \(N\) là tổng số văn bản, \(df_t\) là số văn bản có chứa từ \(t\).

- **Trọng số TF–IDF**:

\[
w_{t,d} = tf_{t,d} \cdot idf_t
\]

Trong code:

- **Spam**:
  - `TfidfVectorizer(max_features=5000, ngram_range=(1, 2))`
  - Sử dụng uni-gram và bi-gram để bắt các cụm như “free money”, “claim now”.
- **News**:
  - `TfidfVectorizer(max_features=8000, ngram_range=(1, 3), stop_words=VIETNAMESE_STOPWORDS)`
  - Dùng danh sách stopwords tiếng Việt (`VIETNAMESE_STOPWORDS`) để loại bỏ từ ít thông tin.

### 8.3 Mô hình Spam: Naive Bayes / Logistic Regression

Trong `train_model.py`:

```python
SPAM_MODEL_TYPE = 'naive_bayes'  # hoặc 'logistic_regression'
```

- **Naive Bayes (mặc định)**:

\[
\hat{y} = \arg\max_c P(c) \prod_{i=1}^{n} P(w_i \mid c)
\]

trong đó:

- \(P(c)\) là xác suất tiên nghiệm của lớp \(c\) (Spam / Not Spam).
- \(P(w_i \mid c)\) là xác suất điều kiện của từ \(w_i\) trong lớp \(c\).

- **Logistic Regression (nhị phân)**:

\[
P(y=1 \mid x) = \sigma(z) = \frac{1}{1 + e^{-z}},\quad z = w^T x + b
\]

- Nếu \(P(y=1 \mid x) \ge 0.5\) → dự đoán Spam, ngược lại Not Spam.
- Trong sklearn: dùng `LogisticRegression(max_iter=1000, solver='lbfgs')`.

- **Huấn luyện & đánh giá**:
  - Tập dữ liệu sau cân bằng được chia `train_test_split` với `test_size=0.2`, `stratify=y`.
  - Huấn luyện trên tập train.
  - Đánh giá trên tập test: **Accuracy**, **F1-score** và `classification_report` (Not Spam / Spam).
  - Nếu dữ liệu quá nhỏ → có thể bỏ test set, huấn luyện trên toàn bộ.

- **Lưu model**:
  - `backend/app/models/spam_model.pkl`
  - `backend/app/models/spam_vectorizer.pkl`

### 8.4 Mô hình News: Multinomial Logistic Regression (Softmax)

News dùng **Logistic Regression đa lớp** với **Softmax**:

1. **Tính điểm (logit)** cho từng lớp \(j\):

\[
z_j = w_j^T x + b_j
\]

2. **Softmax**:

\[
P(y=j \mid x) = \frac{e^{z_j}}{\sum_{k=1}^{K} e^{z_k}}
\]

3. **Dự đoán**:

\[
\hat{y} = \arg\max_j P(y=j \mid x)
\]

Trong code:

- Map nhãn động:

```python
unique_labels = sorted(news_data["Nhãn/Label"].unique())
label_map = {label: idx for idx, label in enumerate(unique_labels)}
```

- Mô hình:

```python
LogisticRegression(
    max_iter=1000,
    random_state=42,
    solver='lbfgs',
    multi_class='multinomial'  # khi khả dụng
)
```

- Đánh giá:
  - Nếu dữ liệu đủ lớn: chia train/test (tương tự spam).
  - Tính **Accuracy**, **F1-score (weighted)**.
  - Dùng `classification_report` trên những lớp thực sự xuất hiện trong test set.

- Lưu model:
  - `backend/app/models/news_model.pkl`
  - `backend/app/models/news_vectorizer.pkl`
  - Trong object model có thêm `label_map` để ánh xạ ngược index → tên nhãn khi dự đoán.

### 8.5 Tóm tắt pipeline huấn luyện

1. Đọc `dataset.xlsx` (nếu không có → dùng dữ liệu mẫu cứng trong code).
2. Chuẩn hóa tên cột, loại bỏ bản ghi thiếu nội dung / nhãn.
3. Tách thành:
   - Tập spam: nhãn `Spam` / `Not Spam`.
   - Tập news: mọi nhãn còn lại.
4. Cân bằng dữ liệu từng tập bằng resampling.
5. Tiền xử lý văn bản với `clean_text`.
6. Biểu diễn TF–IDF (tham số riêng cho spam/news).
7. Chia train/test (khi dữ liệu đủ).
8. Huấn luyện mô hình tương ứng:
   - Spam: Naive Bayes hoặc Logistic Regression.
   - News: Multinomial Logistic Regression (Softmax).
9. Đánh giá bằng Accuracy, F1-score, Classification Report (log ra console).
10. Lưu model + vectorizer vào `backend/app/models` để backend load khi chạy API.

> Ghi chú: Đối với báo cáo học phần, có thể trích trực tiếp phần 8 này (kèm thêm hình minh họa / bảng thống kê kết quả) để mô tả chi tiết mô hình và công thức.
