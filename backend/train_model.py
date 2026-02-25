"""
Training script for Spam and News Classification Models

Mathematical Formulas:

1. SPAM CLASSIFICATION (Binary - 2 classes):
   Option A: Naive Bayes
   y^ = argmax_c P(c) * ∏P(w_i|c)
   
   Option B: Logistic Regression (Sigmoid)
   P(y=1|x) = 1 / (1 + e^(-z))
   where z = w^T * x + b
   
2. NEWS CLASSIFICATION (Multi-class - 5 classes):
   Softmax with Logistic Regression
   P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
   where z_j = w_j^T * x + b_j
   y^ = argmax_j P(y=j|x)

Dataset Format:
- Excel file with columns: "STT", "Nội Dung", "Nhãn/Label"
- Spam labels: "Spam", "Not Spam"
- News labels: "Thể thao", "Chính trị", "Kinh tế", "Công nghệ", "Giải trí"
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.utils import resample
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# Create models directory if it doesn't exist
models_dir = Path(__file__).parent / "app" / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# Configuration
SPAM_MODEL_TYPE = 'naive_bayes'  # Options: 'naive_bayes' or 'logistic_regression'
DATASET_PATH = Path(__file__).parent / "dataset.xlsx"  # Path to Excel file
USE_EXCEL = True  # Set to False to use sample data

# Label definitions
SPAM_LABELS = ["Spam", "Not Spam"]
NEWS_LABELS = ["Thể thao", "Chính trị", "Kinh tế", "Công nghệ", "Giải trí"]

def load_data_from_excel(file_path):
    """
    Load and clean data from Excel file
    
    Expected columns:
    - STT (optional)
    - Nội Dung (text content)
    - Nhãn/Label (label)
    """
    try:
        # Try reading Excel file
        data = pd.read_excel(file_path)
        print(f"✅ Loaded data from {file_path}")
        print(f"   Total rows: {len(data)}")
        
        # Check required columns
        required_cols = ["Nội Dung", "Nhãn/Label"]
        if not all(col in data.columns for col in required_cols):
            # Try alternative column names
            if "Nội dung" in data.columns:
                data = data.rename(columns={"Nội dung": "Nội Dung"})
            if "Label" in data.columns:
                data = data.rename(columns={"Label": "Nhãn/Label"})
            if "Nhãn" in data.columns:
                data = data.rename(columns={"Nhãn": "Nhãn/Label"})
        
        # Clean data
        data = data.dropna(subset=["Nội Dung", "Nhãn/Label"])  # Remove rows with empty content or label
        data["Nội Dung"] = data["Nội Dung"].astype(str)
        data["Nhãn/Label"] = data["Nhãn/Label"].str.strip()
        
        # Remove empty strings
        data = data[data["Nội Dung"].str.len() > 0]
        data = data[data["Nhãn/Label"].str.len() > 0]
        
        print(f"   After cleaning: {len(data)} rows")
        print(f"\n📊 Label distribution:")
        print(data["Nhãn/Label"].value_counts())
        
        return data
        
    except FileNotFoundError:
        print(f"⚠️  File not found: {file_path}")
        print("   Using sample data instead...")
        return None
    except Exception as e:
        print(f"⚠️  Error reading Excel file: {e}")
        print("   Using sample data instead...")
        return None

def balance_data(df, label_column, min_samples_per_class=None):
    """
    Balance dataset by resampling minority classes
    
    Args:
        df: DataFrame with data
        label_column: Name of label column
        min_samples_per_class: Minimum samples per class (default: max class count)
    
    Returns:
        Balanced DataFrame
    """
    label_counts = df[label_column].value_counts()
    
    if min_samples_per_class is None:
        min_samples_per_class = label_counts.max()
    
    print(f"\n⚖️  Balancing data...")
    print(f"   Target samples per class: {min_samples_per_class}")
    
    balanced_dfs = []
    
    for label in df[label_column].unique():
        label_data = df[df[label_column] == label]
        current_count = len(label_data)
        
        if current_count < min_samples_per_class:
            # Upsample minority class
            label_data_resampled = resample(
                label_data,
                replace=True,
                n_samples=min_samples_per_class,
                random_state=42
            )
            print(f"   {label}: {current_count} → {min_samples_per_class} (upsampled)")
        else:
            # Downsample majority class
            label_data_resampled = resample(
                label_data,
                replace=False,
                n_samples=min_samples_per_class,
                random_state=42
            )
            print(f"   {label}: {current_count} → {min_samples_per_class} (downsampled)")
        
        balanced_dfs.append(label_data_resampled)
    
    balanced_df = pd.concat(balanced_dfs, ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    
    return balanced_df

def get_sample_spam_data():
    """Fallback sample data for Spam classification"""
    return [
        # Spam examples
        ("You won a free iPhone! Click here now!", "Spam"),
        ("Congratulations! You've been selected for a $1000 prize!", "Spam"),
        ("URGENT: Claim your reward now!", "Spam"),
        ("Free money! No strings attached!", "Spam"),
        ("Click here to claim your prize!", "Spam"),
        ("You have won $5000! Reply now!", "Spam"),
        ("Limited time offer! Buy now!", "Spam"),
        ("Act now! Special discount for you!", "Spam"),
        ("Get rich quick! Work from home!", "Spam"),
        ("Exclusive offer just for you! Don't miss out!", "Spam"),
        
        # Not Spam examples - Academic/Formal emails
        ("Hello, how are you doing today?", "Not Spam"),
        ("I wanted to follow up on our meeting yesterday.", "Not Spam"),
        ("Can we schedule a call for next week?", "Not Spam"),
        ("Thank you for your email. I'll get back to you soon.", "Not Spam"),
        ("The project deadline is approaching.", "Not Spam"),
        ("Let me know if you have any questions.", "Not Spam"),
        ("I hope you're having a great day!", "Not Spam"),
        ("Please find attached the document you requested.", "Not Spam"),
        ("Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với.", "Not Spam"),
        ("Thầy cho em hỏi về deadline nộp bài tập ạ.", "Not Spam"),
        ("Em xin cảm ơn thầy đã phản hồi email của em.", "Not Spam"),
        ("Em muốn đăng ký học phần này, thầy có thể hướng dẫn em không ạ?", "Not Spam"),
        ("Em gửi file báo cáo như thầy yêu cầu, thầy xem giúp em ạ.", "Not Spam"),
        ("Thầy có thể giải thích thêm về đề tài này không ạ?", "Not Spam"),
        ("Em xin lỗi vì đã trả lời email muộn.", "Not Spam"),
        ("Em muốn xin phép nghỉ học buổi tới ạ.", "Not Spam"),
    ]

def get_sample_news_data():
    """Fallback sample data for News classification"""
    return [
        ("Messi ghi bàn trong trận chung kết World Cup", "Thể thao"),
        ("Đội tuyển Việt Nam giành chiến thắng", "Thể thao"),
        ("Ronaldo lập hat-trick trong trận đấu", "Thể thao"),
        ("Giải bóng đá quốc gia khai mạc", "Thể thao"),
        ("Vận động viên phá kỷ lục thế giới", "Thể thao"),
        ("Quốc hội thông qua luật mới", "Chính trị"),
        ("Chủ tịch nước gặp gỡ lãnh đạo các nước", "Chính trị"),
        ("Hội nghị cấp cao diễn ra tại Hà Nội", "Chính trị"),
        ("Chính phủ ban hành nghị định mới", "Chính trị"),
        ("Bộ trưởng phát biểu tại hội nghị", "Chính trị"),
        ("GDP tăng trưởng 5% trong quý này", "Kinh tế"),
        ("Thị trường chứng khoán tăng điểm", "Kinh tế"),
        ("Ngân hàng giảm lãi suất", "Kinh tế"),
        ("Xuất khẩu tăng mạnh trong tháng", "Kinh tế"),
        ("Doanh nghiệp đầu tư vào công nghệ", "Kinh tế"),
        ("AI thay đổi cách làm việc", "Công nghệ"),
        ("Công ty công nghệ ra mắt sản phẩm mới", "Công nghệ"),
        ("Blockchain ứng dụng trong tài chính", "Công nghệ"),
        ("Startup công nghệ gọi vốn thành công", "Công nghệ"),
        ("5G được triển khai tại các thành phố", "Công nghệ"),
        ("Ca sĩ nổi tiếng tổ chức concert", "Giải trí"),
        ("Phim mới ra mắt đạt doanh thu cao", "Giải trí"),
        ("Diễn viên nhận giải thưởng điện ảnh", "Giải trí"),
        ("Chương trình truyền hình mới lên sóng", "Giải trí"),
        ("Nghệ sĩ biểu diễn tại lễ hội âm nhạc", "Giải trí"),
    ]

def train_spam_model(data=None):
    """
    Train spam classification model using Naive Bayes or Logistic Regression
    
    Naive Bayes Formula:
    y^ = argmax_c P(c) * ∏(i=1 to n) P(w_i|c)
    
    Logistic Regression Formula (Binary):
    P(y=1|x) = 1 / (1 + e^(-(w^T*x + b)))
    y^ = 1 if P(y=1|x) >= 0.5, else 0
    """
    print("=" * 60)
    print("Training Spam Classification Model")
    print(f"Model Type: {SPAM_MODEL_TYPE.upper()}")
    print("=" * 60)
    
    # Load data
    if data is not None:
        # Filter spam data from Excel
        spam_data = data[data["Nhãn/Label"].isin(SPAM_LABELS)].copy()
        
        if len(spam_data) == 0:
            print("⚠️  No spam data found in Excel. Using sample data...")
            spam_data = pd.DataFrame(get_sample_spam_data(), columns=['Nội Dung', 'Nhãn/Label'])
        else:
            print(f"✅ Found {len(spam_data)} spam samples in Excel")
            # Balance data
            spam_data = balance_data(spam_data, "Nhãn/Label")
    else:
        print("📝 Using sample data...")
        spam_data = pd.DataFrame(get_sample_spam_data(), columns=['Nội Dung', 'Nhãn/Label'])
    
    # Map labels to binary (0: Not Spam, 1: Spam)
    label_map = {"Not Spam": 0, "Spam": 1}
    spam_data['label'] = spam_data['Nhãn/Label'].map(label_map)
    
    X = spam_data['Nội Dung']
    y = spam_data['label']
    
    print(f"\n📊 Final dataset:")
    print(f"   Total samples: {len(X)}")
    print(f"   Spam: {sum(y == 1)}")
    print(f"   Not Spam: {sum(y == 0)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train model
    if SPAM_MODEL_TYPE == 'naive_bayes':
        model = MultinomialNB(alpha=1.0)
        print("\n📐 Using Naive Bayes: y^ = argmax_c P(c) * ∏P(w_i|c)")
    else:
        model = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
        print("\n📐 Using Logistic Regression: P(y=1|x) = 1 / (1 + e^(-z))")
    
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    if X_test_vec is not None and len(y_test) > 0:
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"\n📈 Results:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1-Score: {f1:.4f}")
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Not Spam', 'Spam']))
    else:
        print("\n⚠️  No test data available (dataset too small). Model trained on all data.")
    
    # Save model
    model_path = models_dir / "spam_model.pkl"
    vectorizer_path = models_dir / "spam_vectorizer.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print(f"\n💾 Model saved:")
    print(f"   {model_path}")
    print(f"   {vectorizer_path}")
    print("=" * 60)

def train_news_model(data=None):
    """
    Train news classification model using Logistic Regression with Softmax
    
    Softmax Formula (Multi-class):
    Step 1: Calculate scores for each class
    z_j = w_j^T * x + b_j  (for j = 1 to 5)
    
    Step 2: Apply Softmax
    P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
    
    Step 3: Predict class with highest probability
    y^ = argmax_j P(y=j|x)
    """
    print("\n" + "=" * 60)
    print("Training News Classification Model")
    print("Using Softmax (Multi-class Logistic Regression)")
    print("=" * 60)
    
    # Load data
    if data is not None:
        # Filter news data from Excel
        news_data = data[data["Nhãn/Label"].isin(NEWS_LABELS)].copy()
        
        if len(news_data) == 0:
            print("⚠️  No news data found in Excel. Using sample data...")
            news_data = pd.DataFrame(get_sample_news_data(), columns=['Nội Dung', 'Nhãn/Label'])
        else:
            print(f"✅ Found {len(news_data)} news samples in Excel")
            # Balance data
            news_data = balance_data(news_data, "Nhãn/Label")
    else:
        print("📝 Using sample data...")
        news_data = pd.DataFrame(get_sample_news_data(), columns=['Nội Dung', 'Nhãn/Label'])
    
    # Map labels to indices
    label_map = {label: idx for idx, label in enumerate(NEWS_LABELS)}
    news_data['label'] = news_data['Nhãn/Label'].map(label_map)
    
    X = news_data['Nội Dung']
    y = news_data['label']
    
    print(f"\n📊 Final dataset:")
    print(f"   Total samples: {len(X)}")
    for label, idx in label_map.items():
        print(f"   {label}: {sum(y == idx)}")
    
    # Split data
    # Adjust test_size if data is too small
    min_samples_per_class = y.value_counts().min()
    if min_samples_per_class < 2:
        # If any class has less than 2 samples, use all data for training
        print("⚠️  Warning: Some classes have too few samples. Using all data for training.")
        X_train, X_test, y_train, y_test = X, X[:0], y, y[:0]
    elif len(X) < 20:
        # For very small datasets, use smaller test size or no test split
        print("⚠️  Warning: Dataset too small. Using all data for training.")
        X_train, X_test, y_train, y_test = X, X[:0], y, y[:0]
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    
    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    if len(X_test) > 0:
        X_test_vec = vectorizer.transform(X_test)
    else:
        X_test_vec = None
    
    # Train model with Softmax
    # For multi-class, LogisticRegression automatically uses softmax
    # Note: In newer sklearn versions, multi_class parameter may not be needed
    try:
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            multi_class='multinomial'
        )
    except TypeError:
        # For newer sklearn versions without multi_class parameter
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
    print("\n📐 Softmax: P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)")
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    if X_test_vec is not None and len(y_test) > 0:
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"\n📈 Results:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1-Score (weighted): {f1:.4f}")
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=NEWS_LABELS))
    else:
        print("\n⚠️  No test data available (dataset too small). Model trained on all data.")
    
    # Save model
    model_path = models_dir / "news_model.pkl"
    vectorizer_path = models_dir / "news_vectorizer.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print(f"\n💾 Model saved:")
    print(f"   {model_path}")
    print(f"   {vectorizer_path}")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🚀 Starting Model Training...\n")
    
    # Load data from Excel if available
    data = None
    if USE_EXCEL and DATASET_PATH.exists():
        data = load_data_from_excel(DATASET_PATH)
    
    # Train both models
    train_spam_model(data)
    train_news_model(data)
    
    print("\n✅ Training completed successfully!")
    print("\nYou can now start the API server.")
