# 🔧 Troubleshooting - Model Not Available

## ❌ Lỗi: "Model not available. Please train the model first."

### ✅ Giải pháp 1: Kiểm tra models có tồn tại

```bash
cd backend
python -c "from pathlib import Path; print(list(Path('app/models').glob('*.pkl')))"
```

Nếu không có files, chạy training:
```bash
python train_model.py
```

### ✅ Giải pháp 2: Kiểm tra models có load được không

```bash
cd backend
python -c "from app.services.spam_service import spam_classifier; print('Loaded:', spam_classifier._model_loaded)"
```

### ✅ Giải pháp 3: Chạy từ đúng thư mục

**QUAN TRỌNG:** Luôn chạy server từ thư mục `backend/`:

```bash
cd backend
uvicorn app.main:app --reload
```

**KHÔNG chạy từ thư mục gốc:**
```bash
# ❌ SAI
cd PTHTTM
uvicorn backend.app.main:app --reload

# ✅ ĐÚNG
cd backend
uvicorn app.main:app --reload
```

### ✅ Giải pháp 4: Kiểm tra đường dẫn models

Models phải ở: `backend/app/models/`

Cấu trúc đúng:
```
backend/
├── app/
│   ├── models/
│   │   ├── spam_model.pkl
│   │   ├── spam_vectorizer.pkl
│   │   ├── news_model.pkl
│   │   └── news_vectorizer.pkl
```

### ✅ Giải pháp 5: Retrain models

Nếu models bị lỗi, train lại:

```bash
cd backend
python train_model.py
```

Kiểm tra output có thông báo:
```
✅ Model saved: ...
✅ Vectorizer saved: ...
```

### ✅ Giải pháp 6: Kiểm tra logs

Khi chạy server, xem console output:
- Nếu thấy: `✅ Spam model loaded successfully` → OK
- Nếu thấy: `⚠️  Spam model not found` → Cần train lại

### ✅ Giải pháp 7: Test trực tiếp

```bash
cd backend
python -c "from app.services.spam_service import spam_classifier; result = spam_classifier.predict('test'); print(result)"
```

Nếu lỗi ở đây, vấn đề là models.
Nếu OK ở đây nhưng lỗi khi chạy server, vấn đề là đường dẫn hoặc import.

## 🔍 Debug Steps

1. **Kiểm tra models tồn tại:**
   ```bash
   ls backend/app/models/*.pkl
   ```

2. **Test import:**
   ```bash
   cd backend
   python -c "from app.services.spam_service import spam_classifier"
   ```

3. **Test prediction:**
   ```bash
   cd backend
   python -c "from app.services.spam_service import spam_classifier; print(spam_classifier.predict('test'))"
   ```

4. **Chạy server và xem logs:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   Xem console có thông báo load models không.

## 📝 Checklist

- [ ] Models đã được train (`python train_model.py`)
- [ ] Files `.pkl` tồn tại trong `backend/app/models/`
- [ ] Chạy server từ thư mục `backend/`
- [ ] Console hiển thị "✅ Spam model loaded successfully"
- [ ] Console hiển thị "✅ News model loaded successfully"

## 💡 Lưu ý

- Models **KHÔNG cần database** để hoạt động
- Database chỉ để lưu lịch sử
- Nếu models load OK, API sẽ hoạt động dù không có database
