# 📐 Mathematical Formulas for Text Classification

Tài liệu này giải thích các công thức toán học được sử dụng trong hệ thống phân loại văn bản.

## 📧 1. Spam Classification (Phân loại nhị phân - 2 lớp)

### Option A: Naive Bayes (Khuyến nghị cho Spam)

**Công thức dự đoán:**
```
ŷ = argmax_c P(c|x)
```

**Theo định lý Bayes:**
```
P(c|x) = P(x|c) * P(c) / P(x)
```

**Vì P(x) giống nhau cho mọi lớp, ta chỉ cần:**
```
ŷ = argmax_c P(x|c) * P(c)
```

**Với văn bản có nhiều từ w₁, w₂, ..., wₙ:**
```
P(x|c) = ∏(i=1 to n) P(w_i|c)
```

**Công thức cuối cùng:**
```
ŷ = argmax_c P(c) * ∏(i=1 to n) P(w_i|c)
```

**Giải thích:**
- `P(c)`: Xác suất tiên nghiệm của lớp c (Spam hoặc Not Spam)
- `P(w_i|c)`: Xác suất từ w_i xuất hiện trong lớp c
- Giả định Naive: Các từ độc lập với nhau khi biết lớp (conditional independence)

**Ưu điểm:**
- Phù hợp với dữ liệu nhỏ
- Nhanh và hiệu quả
- Hoạt động tốt với spam detection

---

### Option B: Logistic Regression (Hồi quy Logistic)

**Hàm tuyến tính:**
```
z = w^T * x + b
```

**Hàm Sigmoid (cho bài toán nhị phân):**
```
P(y=1|x) = 1 / (1 + e^(-z))
         = 1 / (1 + e^(-(w^T*x + b)))
```

**Dự đoán:**
```
ŷ = {
    1  nếu P(y=1|x) ≥ 0.5
    0  ngược lại
}
```

**Giải thích:**
- `w`: Vector trọng số (weight vector)
- `x`: Vector đặc trưng TF-IDF
- `b`: Hệ số bias
- Sigmoid chuyển đổi điểm số thành xác suất (0 đến 1)

**Ưu điểm:**
- Dễ giải thích
- Hoạt động tốt với dữ liệu lớn
- Có thể thêm regularization

---

## 📰 2. News Classification (Phân loại đa lớp - 5 lớp)

### Softmax với Logistic Regression

**Bước 1: Tính điểm cho mỗi lớp**
```
z_j = w_j^T * x + b_j
```
với j = 1, 2, 3, 4, 5 (tương ứng: Thể thao, Chính trị, Kinh tế, Công nghệ, Giải trí)

**Bước 2: Áp dụng Softmax**
```
P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
```

**Bước 3: Chọn lớp có xác suất cao nhất**
```
ŷ = argmax_j P(y=j|x)
```

**Giải thích:**
- `z_j`: Điểm số tuyến tính cho lớp j
- Softmax chuẩn hóa các điểm số thành xác suất (tổng = 1)
- Lớp có xác suất cao nhất được chọn làm dự đoán

**Ví dụ với 5 lớp:**
```
P(y=Thể thao|x) = e^(z₁) / (e^(z₁) + e^(z₂) + e^(z₃) + e^(z₄) + e^(z₅))
P(y=Chính trị|x) = e^(z₂) / (e^(z₁) + e^(z₂) + e^(z₃) + e^(z₄) + e^(z₅))
...
```

**Ưu điểm:**
- Phù hợp cho phân loại đa lớp
- Xác suất được chuẩn hóa (tổng = 1)
- Dễ giải thích kết quả

---

## 🔄 3. Quy trình xử lý

### Vector hóa TF-IDF

**TF (Term Frequency):**
```
TF(t,d) = số lần từ t xuất hiện trong văn bản d / tổng số từ trong d
```

**IDF (Inverse Document Frequency):**
```
IDF(t,D) = log(N / số văn bản chứa từ t)
```
với N là tổng số văn bản trong tập dữ liệu D

**TF-IDF:**
```
TF-IDF(t,d,D) = TF(t,d) * IDF(t,D)
```

**Vector đặc trưng:**
```
x = [TF-IDF(w₁), TF-IDF(w₂), ..., TF-IDF(w_n)]
```

---

## 📊 4. So sánh các phương pháp

| Phương pháp | Loại bài toán | Công thức chính | Ưu điểm |
|------------|---------------|-----------------|---------|
| **Naive Bayes** | Nhị phân/Đa lớp | P(c) * ∏P(w_i\|c) | Nhanh, phù hợp spam |
| **Logistic Regression (Sigmoid)** | Nhị phân | 1 / (1 + e^(-z)) | Dễ giải thích, tốt với dữ liệu lớn |
| **Logistic Regression (Softmax)** | Đa lớp | e^(z_j) / Σe^(z_k) | Phù hợp phân loại nhiều lớp |

---

## 🎯 5. Implementation trong code

### Spam Classification
```python
# Naive Bayes
model = MultinomialNB()
# Hoặc
# Logistic Regression
model = LogisticRegression()
```

### News Classification
```python
# Softmax (Multi-class Logistic Regression)
model = LogisticRegression(multi_class='multinomial', solver='lbfgs')
```

---

## 📚 Tài liệu tham khảo

- **Naive Bayes**: Dựa trên định lý Bayes và giả định độc lập điều kiện
- **Logistic Regression**: Generalized Linear Model với hàm liên kết logit
- **Softmax**: Tổng quát hóa của hàm sigmoid cho nhiều lớp
- **TF-IDF**: Phương pháp vector hóa văn bản phổ biến

---

## 🔍 Chi tiết kỹ thuật

### Training Process

1. **Tiền xử lý**: Làm sạch văn bản, loại bỏ ký tự đặc biệt
2. **Vector hóa**: Chuyển đổi văn bản thành vector TF-IDF
3. **Huấn luyện**: Tối ưu hóa tham số w và b
4. **Đánh giá**: Accuracy, F1-score, Classification Report

### Prediction Process

1. **Input**: Văn bản cần phân loại
2. **Preprocessing**: Làm sạch và chuẩn hóa
3. **Vectorization**: Chuyển đổi sang TF-IDF vector
4. **Calculation**: Áp dụng công thức toán học
5. **Output**: Nhãn dự đoán và độ tin cậy

---

**Lưu ý**: Các công thức trên được implement tự động bởi scikit-learn. Code chỉ cần gọi các hàm `fit()` và `predict()`.
