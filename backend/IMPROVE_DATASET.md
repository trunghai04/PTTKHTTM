# 🔧 Cải thiện Dataset để giảm False Positive

## ❌ Vấn đề hiện tại

Với câu: **"Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với."**

Model dự đoán: **Spam (55%)** - Đây là **FALSE POSITIVE**

## 🔍 Nguyên nhân

### 1. Dataset quá ít
- **Hiện tại:** 6 Spam, 7 Not Spam (chỉ 13 mẫu)
- **Cần:** Ít nhất 100-200 mẫu mỗi lớp

### 2. Thiếu dữ liệu email học thuật
- Dataset không có đủ email dạng:
  - Email trao đổi với thầy cô
  - Email đăng ký môn học
  - Email xin phép, cảm ơn

### 3. Threshold quá thấp
- Mặc định: 0.5 (50%)
- Đã cải thiện: 0.65 (65%) - giảm false positive

## ✅ Giải pháp đã áp dụng

### 1. Thêm Threshold (0.65)
```python
# Trước: Spam nếu P >= 0.5
# Sau: Spam nếu P >= 0.65 VÀ P > P(Not Spam)
```

### 2. Warning khi confidence thấp
- Nếu confidence < 70% → hiển thị warning
- Giúp người dùng biết prediction không chắc chắn

### 3. Hiển thị cả 2 probabilities
- `spam_probability`: Xác suất Spam
- `not_spam_probability`: Xác suất Not Spam
- Giúp hiểu rõ hơn về prediction

## 📝 Cách cải thiện Dataset

### Bước 1: Thêm nhiều email học thuật vào Not Spam

Mở file `backend/dataset.xlsx` và thêm các dòng sau:

| STT | Nội Dung | Nhãn/Label |
|-----|----------|------------|
| ... | Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với. | Not Spam |
| ... | Thầy cho em hỏi về deadline nộp bài tập ạ. | Not Spam |
| ... | Em xin cảm ơn thầy đã phản hồi email của em. | Not Spam |
| ... | Em muốn đăng ký học phần này, thầy có thể hướng dẫn em không ạ? | Not Spam |
| ... | Em gửi file báo cáo như thầy yêu cầu, thầy xem giúp em ạ. | Not Spam |
| ... | Thầy có thể giải thích thêm về đề tài này không ạ? | Not Spam |
| ... | Em xin lỗi vì đã trả lời email muộn. | Not Spam |
| ... | Em muốn xin phép nghỉ học buổi tới ạ. | Not Spam |
| ... | Em đã hoàn thành bài tập, thầy xem giúp em ạ. | Not Spam |
| ... | Thầy cho em hỏi về lịch thi cuối kỳ ạ. | Not Spam |

### Bước 2: Thêm nhiều Spam examples

| STT | Nội Dung | Nhãn/Label |
|-----|----------|------------|
| ... | Bạn đã trúng thưởng 1 tỷ đồng! Click ngay! | Spam |
| ... | Giảm giá 90% chỉ hôm nay! Mua ngay! | Spam |
| ... | Bạn có thể kiếm 10 triệu mỗi ngày! | Spam |

### Bước 3: Cân bằng dữ liệu

**Mục tiêu:**
- Spam: 100-200 mẫu
- Not Spam: 100-200 mẫu
- Tỷ lệ: 1:1 (hoặc 0.8:1.2)

### Bước 4: Retrain model

Sau khi thêm dữ liệu:

```bash
cd backend
python train_model.py
```

## 🧪 Test sau khi cải thiện

```bash
cd backend
python -c "from app.services.spam_service import spam_classifier; result = spam_classifier.predict('Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với.'); print(result)"
```

**Kết quả mong đợi:**
- Label: **Not Spam**
- Confidence: **> 70%**
- Warning: **None** (hoặc không có)

## 📊 Phân tích Dataset

Chạy script phân tích:

```bash
cd backend
python analyze_dataset.py
```

Script sẽ cho biết:
- Số lượng mỗi lớp
- Tỷ lệ cân bằng
- Độ dài text trung bình
- Khuyến nghị cải thiện

## 🎯 Tóm tắt

| Vấn đề | Giải pháp | Trạng thái |
|--------|-----------|------------|
| Dataset quá ít | Thêm 100+ mẫu mỗi lớp | ⏳ Cần làm |
| Thiếu email học thuật | Thêm vào Not Spam | ⏳ Cần làm |
| Threshold thấp | Đã nâng lên 0.65 | ✅ Đã làm |
| Không có warning | Đã thêm warning | ✅ Đã làm |
| Không hiển thị probabilities | Đã thêm | ✅ Đã làm |

## 💡 Lưu ý

- **Threshold 0.65** sẽ giảm false positive nhưng có thể tăng false negative
- Nếu muốn strict hơn: tăng lên **0.7 hoặc 0.75**
- Nếu muốn sensitive hơn: giảm xuống **0.6**

Cấu hình threshold trong `backend/app/services/spam_service.py`:
```python
SPAM_THRESHOLD = 0.65  # Điều chỉnh ở đây
```
