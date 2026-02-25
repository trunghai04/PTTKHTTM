# 📊 Hướng dẫn Dataset

## 📁 Cấu trúc File Excel

File Excel cần có các cột sau:

| STT | Nội Dung | Nhãn/Label |
|-----|----------|------------|
| 1   | Win free iPhone | Spam |
| 2   | Họp lúc 8h sáng | Not Spam |
| 3   | Messi ghi bàn | Thể thao |

### ⚠️ Lưu ý quan trọng:

1. **Tên cột chính xác:**
   - `Nội Dung` hoặc `Nội dung` (chứa văn bản)
   - `Nhãn/Label` hoặc `Label` hoặc `Nhãn` (chứa nhãn)

2. **Nhãn hợp lệ:**

   **Spam Classification (2 nhãn):**
   - `Spam`
   - `Not Spam`

   **News Classification (5 nhãn):**
   - `Thể thao`
   - `Chính trị`
   - `Kinh tế`
   - `Công nghệ`
   - `Giải trí`

3. **Không được có:**
   - Dòng trống
   - Ô trống trong cột "Nội Dung" hoặc "Nhãn/Label"
   - Sai chính tả nhãn (vd: "Spamm", "The thao")

## 📍 Đặt file Excel

Đặt file Excel tại: `backend/dataset.xlsx`

Hoặc thay đổi đường dẫn trong `train_model.py`:
```python
DATASET_PATH = Path(__file__).parent / "dataset.xlsx"
```

## ⚖️ Cân bằng dữ liệu

Hệ thống tự động cân bằng dữ liệu:

- **Upsampling**: Tăng số lượng mẫu của lớp thiểu số
- **Downsampling**: Giảm số lượng mẫu của lớp đa số

**Ví dụ:**
```
Spam: 1000 mẫu
Not Spam: 50 mẫu
→ Tự động cân bằng về 1000 mẫu mỗi lớp
```

## 🔍 Kiểm tra dữ liệu

Sau khi load, hệ thống sẽ hiển thị:

```
✅ Loaded data from dataset.xlsx
   Total rows: 1000
   After cleaning: 950 rows

📊 Label distribution:
Spam           500
Not Spam       200
Thể thao       100
Chính trị       80
...
```

## 🚀 Chạy Training

```bash
cd backend
python train_model.py
```

Nếu không có file Excel, hệ thống sẽ tự động dùng sample data.

## 📝 Ví dụ File Excel

Tạo file `backend/dataset.xlsx` với nội dung:

| STT | Nội Dung | Nhãn/Label |
|-----|----------|------------|
| 1 | You won a free iPhone! | Spam |
| 2 | Hello, how are you? | Not Spam |
| 3 | Messi ghi bàn trong trận chung kết | Thể thao |
| 4 | Quốc hội thông qua luật mới | Chính trị |
| 5 | GDP tăng trưởng 5% | Kinh tế |
| 6 | AI thay đổi cách làm việc | Công nghệ |
| 7 | Ca sĩ nổi tiếng tổ chức concert | Giải trí |

## ⚙️ Cấu hình

Trong `train_model.py`:

```python
# Sử dụng Excel hay sample data
USE_EXCEL = True  # False để dùng sample data

# Đường dẫn file Excel
DATASET_PATH = Path(__file__).parent / "dataset.xlsx"

# Model type cho Spam
SPAM_MODEL_TYPE = 'naive_bayes'  # hoặc 'logistic_regression'
```

## 🐛 Troubleshooting

### Lỗi: File not found
- Kiểm tra đường dẫn file Excel
- Đảm bảo file có tên đúng: `dataset.xlsx`
- Đặt file trong thư mục `backend/`

### Lỗi: No spam/news data found
- Kiểm tra nhãn có đúng chính tả không
- Xem danh sách nhãn hợp lệ ở trên
- Đảm bảo có ít nhất 1 mẫu cho mỗi nhãn

### Lỗi: Empty cells
- Xóa các dòng có ô trống
- Đảm bảo cột "Nội Dung" và "Nhãn/Label" đều có giá trị

## 📚 Tài liệu tham khảo

- Xem `MATHEMATICAL_FORMULAS.md` để hiểu công thức toán học
- Xem `README_FORMULAS.md` để xem tóm tắt công thức
