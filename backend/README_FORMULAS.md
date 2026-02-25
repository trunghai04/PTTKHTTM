# 📐 Tóm tắt Công thức Toán học

## 🎯 Quick Reference

### 📧 Spam Classification (2 lớp)

**Naive Bayes (Mặc định):**
```
ŷ = argmax_c P(c) * ∏(i=1 to n) P(w_i|c)
```

**Logistic Regression:**
```
P(y=1|x) = 1 / (1 + e^(-(w^T*x + b)))
ŷ = 1 nếu P(y=1|x) ≥ 0.5, else 0
```

### 📰 News Classification (5 lớp)

**Softmax:**
```
z_j = w_j^T * x + b_j
P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
ŷ = argmax_j P(y=j|x)
```

## ⚙️ Cấu hình

Trong `train_model.py`, bạn có thể chọn model cho Spam:

```python
SPAM_MODEL_TYPE = 'naive_bayes'  # hoặc 'logistic_regression'
```

## 📚 Chi tiết

Xem file `MATHEMATICAL_FORMULAS.md` để biết chi tiết đầy đủ về các công thức.
