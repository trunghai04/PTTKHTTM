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

Pipeline: Train và inference (spam_service.predict / news_service.predict) đều dùng
clean_text() → cùng phân phối, không bị mismatch.
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, f1_score, confusion_matrix
from sklearn.utils import resample
from pathlib import Path
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV

from app.utils.preprocess import clean_text
from app.database.db import SessionLocal
from app.database.models import Prediction, PredictionType

warnings.filterwarnings('ignore')

# Create models directory if it doesn't exist
models_dir = Path(__file__).parent / "app" / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# Create reports directory for evaluation plots
reports_dir = Path(__file__).parent / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

# Configuration
# Auto-select best spam model by validation F1 for better robustness across datasets.
SPAM_MODEL_TYPE = 'auto'  # Options: 'auto', 'naive_bayes', 'logistic_regression'

# Main Excel dataset (có thể có cột STT hoặc không, đều OK)
DATASET_PATH = Path(__file__).parent / "dataset.xlsx"
USE_EXCEL = True  # Set to False to ignore Excel

# Optional CSV dataset (không cần cột STT).
# Yêu cầu ONLY 2 cột chính: "Nội Dung", "Nhãn/Label".
CSV_DATASET_PATH = Path(__file__).parent / "dataset.csv"
USE_CSV = True  # Set to False to ignore CSV

# Label definitions
# For spam we keep fixed labels. For news we now
# infer labels dynamically from the Excel file
# (all labels that are not spam).
SPAM_LABELS = ["Spam", "Not Spam"]
NEWS_LABELS = ["Thể thao", "Chính trị", "Kinh tế", "Công nghệ", "Giải trí"]  # kept for docs / sample data

# Ngưỡng dataset nhỏ: dùng min_df=1, sublinear_tf=False để tránh mất từ vựng / overfit
SMALL_DATASET_THRESHOLD = 200
MIN_NEWS_CLASS_SAMPLES = 20

# Vietnamese stopwords (common words that add little meaning for classification)
VIETNAMESE_STOPWORDS = {
    "và", "là", "của", "có", "được", "cho", "với", "trong", "này", "đó",
    "các", "một", "những", "đã", "sẽ", "khi", "như", "về", "từ", "đến",
    "hay", "hoặc", "nếu", "thì", "mà", "để", "bởi", "theo", "qua", "sau",
    "trước", "trên", "dưới", "ngoài", "trong", "giữa", "cùng", "vì", "do",
    "rằng", "làm", "nên", "ra", "vào", "lên", "xuống", "qua", "lại",
    "rất", "quá", "cũng", "đều", "chỉ", "mới", "đang", "vẫn", "còn",
    "không", "chưa", "chẳng", "nào", "gì", "ai", "đâu", "sao", "thế",
    "năm", "tháng", "ngày", "giờ", "phút", "giây", "hôm", "ngày",
}

def normalize_spam_label(s: str) -> str:
    """Normalize spam/not-spam aliases into canonical labels."""
    low = str(s).lower().strip()
    if low in ("spam", "1", "yes", "true"):
        return "Spam"
    if low in ("not spam", "notspam", "not_spam", "0", "no", "false", "ham"):
        return "Not Spam"
    return str(s).strip()


def deduplicate_by_text(df: pd.DataFrame, text_col: str = "Nội Dung") -> pd.DataFrame:
    """
    Deduplicate dataset by text content to reduce train/test leakage.
    Keep first occurrence to preserve deterministic behavior.
    """
    before = len(df)
    deduped = df.drop_duplicates(subset=[text_col]).reset_index(drop=True)
    removed = before - len(deduped)
    ratio = (removed / before) if before else 0.0
    print(
        f"🧹 Dedup by text: removed {removed}/{before} rows ({ratio:.2%}), remaining {len(deduped)} rows."
    )
    return deduped


def plot_confusion_matrix(cm, class_names, title, save_path):
    """Plot and save confusion matrix heatmap."""
    plt.figure(figsize=(5, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title(title)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"   💾 Saved confusion matrix to: {save_path}")


def plot_accuracy_comparison(model_names, accuracies, title, save_path):
    """Plot and save bar chart comparing model accuracies."""
    plt.figure(figsize=(6, 4))
    plt.bar(model_names, accuracies, color=["#4C72B0", "#55A868"])
    plt.ylim(0, 1)
    for i, acc in enumerate(accuracies):
        plt.text(i, acc + 0.01, f"{acc:.3f}", ha="center")
    plt.title(title)
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"   💾 Saved accuracy comparison chart to: {save_path}")

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
        data["Nhãn/Label"] = data["Nhãn/Label"].astype(str).str.strip()
        
        # Chuẩn hóa nhãn Spam/Not Spam (tránh "spam", "SPAM", " Not Spam " → NaN khi map)
        data["Nhãn/Label"] = data["Nhãn/Label"].apply(normalize_spam_label)
        
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


def load_data_from_csv(file_path):
    """
    Load and clean data from CSV file.

    Không bắt buộc có cột STT.
    Yêu cầu các cột nội dung / nhãn giống Excel:
    - Nội Dung
    - Nhãn/Label
    """
    try:
        # Tolerant parsing for noisy CSV (bad quoting/comma in content).
        # Keep training robust by skipping malformed lines.
        try:
            data = pd.read_csv(file_path, engine="python", on_bad_lines="skip")
        except TypeError:
            # pandas < 2.0 fallback
            data = pd.read_csv(file_path, engine="python", error_bad_lines=False)
        print(f"✅ Loaded CSV data from {file_path}")
        print(f"   Total rows: {len(data)}")

        # Chuẩn hóa tên cột (hỗ trợ cả header không dấu: NoiDung, Label)
        def _norm_col_key(s: str) -> str:
            return (
                str(s)
                .replace("\ufeff", "")
                .strip()
                .lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
            )

        col_aliases = {
            "Nội Dung": [
                "Nội Dung",
                "Nội dung",
                "NoiDung",
                "Noi Dung",
                "noi_dung",
                "content",
                "text",
            ],
            "Nhãn/Label": [
                "Nhãn/Label",
                "Nhan/Label",
                "Nhãn",
                "Nhan",
                "Label",
                "label",
                "category",
            ],
        }
        alias_key_map = {
            _norm_col_key(alias): canonical
            for canonical, aliases in col_aliases.items()
            for alias in aliases
        }

        rename_map = {}
        for col in list(data.columns):
            canonical = alias_key_map.get(_norm_col_key(col))
            if canonical and col != canonical:
                rename_map[col] = canonical
        if rename_map:
            data = data.rename(columns=rename_map)

        required_cols = ["Nội Dung", "Nhãn/Label"]
        if not all(col in data.columns for col in required_cols):
            print(
                f"⚠️  CSV thiếu cột bắt buộc. Cần {required_cols}, hiện có: {list(data.columns)}"
            )
            return None

        # Drop các dòng thiếu nội dung / nhãn
        data = data.dropna(subset=["Nội Dung", "Nhãn/Label"])
        data["Nội Dung"] = data["Nội Dung"].astype(str)
        data["Nhãn/Label"] = data["Nhãn/Label"].astype(str).str.strip()

        # Chuẩn hóa nhãn Spam/Not Spam giống Excel
        data["Nhãn/Label"] = data["Nhãn/Label"].apply(normalize_spam_label)

        # Bỏ dòng rỗng
        data = data[data["Nội Dung"].str.len() > 0]
        data = data[data["Nhãn/Label"].str.len() > 0]

        print(f"   After CSV cleaning: {len(data)} rows")
        print(f"\n📊 CSV Label distribution:")
        print(data["Nhãn/Label"].value_counts())

        return data
    except FileNotFoundError:
        print(f"ℹ️  CSV file not found: {file_path}")
        return None
    except Exception as e:
        print(f"⚠️  Error reading CSV file: {e}")
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


def load_user_feedback_data(
    prediction_type: PredictionType, min_confidence: float = 0.9
):
    """
    Load high-confidence user predictions from the database to use as extra training data.

    - prediction_type: PredictionType.SPAM or PredictionType.NEWS
    - min_confidence: only use rows with confidence >= threshold

    Returns:
        DataFrame with columns ["Nội Dung", "Nhãn/Label"] or None if no data.
    """
    try:
        db = SessionLocal()
        query = (
            db.query(Prediction)
            .filter(
                Prediction.type == prediction_type,
                Prediction.confidence >= float(min_confidence),
            )
            .order_by(Prediction.created_at.desc())
        )

        rows = query.all()
        if not rows:
            print(
                f"ℹ️  No high-confidence {prediction_type.value} user feedback found (min_confidence={min_confidence})."
            )
            return None

        print(
            f"✅ Loaded {len(rows)} high-confidence {prediction_type.value} samples from user feedback (confidence >= {min_confidence})."
        )

        texts = [r.text for r in rows]
        labels = [r.predicted_label for r in rows]
        df = pd.DataFrame({"Nội Dung": texts, "Nhãn/Label": labels})
        return df
    except Exception as e:
        print(f"⚠️  Could not load user feedback data from database: {e}")
        return None
    finally:
        try:
            db.close()
        except Exception:
            pass

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
            # Remove duplicate texts first to avoid leakage, then balance classes.
            spam_data = deduplicate_by_text(spam_data, "Nội Dung")
            # Balance data
            spam_data = balance_data(spam_data, "Nhãn/Label")
    else:
        print("📝 Using sample data...")
        spam_data = pd.DataFrame(get_sample_spam_data(), columns=['Nội Dung', 'Nhãn/Label'])

    # KHÔNG còn tự học từ DB cho Spam nữa.
    # Lý do: dữ liệu trong bảng predictions có thể chứa nhiều mẫu bị gắn nhãn sai
    # (ví dụ biên lai ngân hàng bị model cũ đánh nhầm là Spam). Đưa các mẫu này
    # vào lại tập train sẽ làm mô hình củng cố sai lệch.
    #
    # Nếu sau này bạn có cơ chế review / gán nhãn lại dữ liệu trong DB, ta có thể
    # bật lại việc dùng load_user_feedback_data với tập đã được làm sạch.
    #
    # user_spam_df = load_user_feedback_data(PredictionType.SPAM, min_confidence=0.98)
    # if user_spam_df is not None and not user_spam_df.empty:
    #     print(f"🔁 Augmenting spam dataset with {len(user_spam_df)} user-labelled samples.")
    #     spam_data = pd.concat([spam_data, user_spam_df], ignore_index=True)
    
    # Map labels to binary (0: Not Spam, 1: Spam)
    label_map = {"Not Spam": 0, "Spam": 1}
    spam_data['label'] = spam_data['Nhãn/Label'].map(label_map)
    
    # Kiểm tra nhãn không đúng format → map ra NaN (dataset lỗi)
    na_count = spam_data['label'].isna().sum()
    if na_count > 0:
        print(f"🔴 Lỗi nhãn: {na_count} dòng map ra NaN. Nhãn phải là 'Spam' hoặc 'Not Spam'. Các giá trị khác: {spam_data.loc[spam_data['label'].isna(), 'Nhãn/Label'].unique().tolist()}")
        spam_data = spam_data.dropna(subset=['label'])
        if len(spam_data) == 0:
            raise ValueError("Không còn dòng nào sau khi bỏ nhãn lỗi. Sửa cột Nhãn/Label trong Excel.")
    
    # Apply same preprocessing as inference (phải giống spam_service.predict() → clean_text)
    X = spam_data['Nội Dung'].apply(clean_text)
    y = spam_data['label'].astype(int)
    
    print(f"\n📊 Final dataset:")
    print(f"   Total samples: {len(X)}")
    print(f"   Spam: {sum(y == 1)}")
    print(f"   Not Spam: {sum(y == 0)}")
    print(f"   Label distribution:\n{pd.Series(y).value_counts()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # TF-IDF: min_df=1 để không mất từ vựng khi dataset nhỏ; sublinear_tf chỉ khi đủ dữ liệu
    n_samples = len(X_train)
    use_sublinear_tf = n_samples >= SMALL_DATASET_THRESHOLD
    max_feat = min(5000, max(500, n_samples * 10))  # dataset nhỏ → ít feature, tránh overfit
    vectorizer = TfidfVectorizer(
        max_features=max_feat,
        ngram_range=(1, 2),
        sublinear_tf=use_sublinear_tf,
        min_df=1,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Debug pipeline (90% lỗi dự đoán sai do vocabulary quá nhỏ hoặc label lệch)
    vocab_size = len(vectorizer.vocabulary_)
    print(f"\n🔍 Pipeline debug:")
    print(f"   Vocabulary size: {vocab_size}")
    if vocab_size < 50:
        print(f"   ⚠️  CẢNH BÁO: Vocabulary < 50 → model gần như không học được gì. Kiểm tra min_df hoặc thêm dữ liệu.")
    print(f"   X_train shape: {X_train_vec.shape}")
    print(f"   X_test shape: {X_test_vec.shape}")
    print(f"   Label distribution (train):\n{pd.Series(y_train).value_counts()}")
    
    # Train và so sánh cả 2 model: Naive Bayes vs Logistic Regression
    print("\n🤖 Training and comparing Spam models (Naive Bayes vs Logistic Regression)")
    spam_models = {
        "Naive Bayes": MultinomialNB(alpha=1.0),
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            random_state=42,
            solver='lbfgs',
            class_weight='balanced',
            C=2.0,
        ),
    }
    results = []
    
    for name, clf in spam_models.items():
        print(f"\n--- {name} ---")
        clf.fit(X_train_vec, y_train)
        
        if X_test_vec is not None and len(y_test) > 0:
            y_pred = clf.predict(X_test_vec)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            print(f"Accuracy: {accuracy:.4f}")
            print(f"F1-Score: {f1:.4f}")
            
            # Confusion matrix (text)
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
            print("Confusion Matrix (rows=true, cols=pred):")
            print(cm)
            
            # Confusion matrix heatmap
            cm_path = reports_dir / f"spam_confusion_{name.lower().replace(' ', '_')}.png"
            plot_confusion_matrix(
                cm,
                class_names=["Not Spam", "Spam"],
                title=f"Spam - {name}",
                save_path=cm_path,
            )
            
            # Cross Validation (CV=5 nếu đủ dữ liệu)
            cv_acc = None
            if len(y_train) >= 5:
                scores = cross_val_score(clf, X_train_vec, y_train, cv=5)
                cv_acc = scores.mean()
                print(f"CV Accuracy (5-fold): {cv_acc:.4f}")
            else:
                print("⚠️  Not enough samples for 5-fold cross validation.")
            
            results.append(
                {
                    "Model": name,
                    "Accuracy": accuracy,
                    "F1": f1,
                    "CV_Accuracy": cv_acc,
                }
            )
            
            print("\n📋 Classification Report:")
            print(classification_report(y_test, y_pred, target_names=['Not Spam', 'Spam']))
        else:
            print("⚠️  No test data available (dataset too small). Skipping evaluation and CV.")
    
    # Bảng so sánh tổng hợp
    if results:
        print("\n📊 Spam model comparison (hold-out + cross-validation):")
        header = f"{'Model':<20}{'Accuracy':<12}{'F1':<12}{'CV Accuracy':<12}"
        print(header)
        print("-" * len(header))
        model_names = []
        accuracies = []
        for r in results:
            cv_str = f"{r['CV_Accuracy']:.4f}" if r["CV_Accuracy"] is not None else "-"
            print(f"{r['Model']:<20}{r['Accuracy']:<12.4f}{r['F1']:<12.4f}{cv_str:<12}")
            model_names.append(r["Model"])
            accuracies.append(r["Accuracy"])
        
        # Biểu đồ so sánh Accuracy
        acc_path = reports_dir / "spam_model_accuracy_comparison.png"
        plot_accuracy_comparison(
            model_names,
            accuracies,
            title="Spam Models Accuracy Comparison",
            save_path=acc_path,
        )
    else:
        print("\n⚠️  No evaluation results to compare (dataset too small).")
    
    # Chọn model deploy cuối cùng
    selected_model_name = "Logistic Regression"
    if results and SPAM_MODEL_TYPE == "auto":
        selected_model_name = max(results, key=lambda r: r["F1"])["Model"]
        print(f"\n📐 Auto-selected best spam model by F1: {selected_model_name}.")
    elif SPAM_MODEL_TYPE == "naive_bayes":
        selected_model_name = "Naive Bayes"
        print("\n📐 Using Naive Bayes as final deployed model.")
    else:
        selected_model_name = "Logistic Regression"
        print("\n📐 Using Logistic Regression as final deployed model.")
    model = spam_models[selected_model_name]

    # Calibrate probabilities so "confidence" is less overconfident.
    # This helps confidence behave better on out-of-domain / long-form inputs.
    try:
        min_class = int(pd.Series(y_train).value_counts().min())
        if len(y_train) >= 300 and min_class >= 50:
            print("\n🧪 Calibrating spam model probabilities (sigmoid)...")
            calibrated = CalibratedClassifierCV(model, method="sigmoid", cv=3)
            calibrated.fit(X_train_vec, y_train)
            model = calibrated
            print("   ✅ Calibration applied.")
        else:
            print("\nℹ️  Skipping calibration (dataset too small / imbalanced for stable calibration).")
    except Exception as e:
        print(f"\n⚠️  Calibration skipped due to error: {e}")
    
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
        # Treat all NON-spam labels as news categories.
        news_data = data[~data["Nhãn/Label"].isin(SPAM_LABELS)].copy()
        
        if len(news_data) == 0:
            print("⚠️  No news data found in Excel (only spam labels present). Using sample data...")
            news_data = pd.DataFrame(get_sample_news_data(), columns=['Nội Dung', 'Nhãn/Label'])
        else:
            print(f"✅ Found {len(news_data)} news samples in Excel")
            detected_labels = sorted(news_data["Nhãn/Label"].unique())
            print(f"   Detected news labels: {detected_labels}")
            # Remove duplicate texts first to avoid leakage, then balance classes.
            news_data = deduplicate_by_text(news_data, "Nội Dung")
            # Drop tiny/noisy classes from bad labels before balancing.
            class_counts = news_data["Nhãn/Label"].value_counts()
            rare_labels = class_counts[class_counts < MIN_NEWS_CLASS_SAMPLES].index.tolist()
            if rare_labels:
                print(
                    f"🧪 Removing rare/noisy news labels (<{MIN_NEWS_CLASS_SAMPLES} samples): {rare_labels}"
                )
                news_data = news_data[~news_data["Nhãn/Label"].isin(rare_labels)].copy()
                if len(news_data) == 0:
                    raise ValueError(
                        "News data became empty after filtering rare labels. Check dataset labels."
                    )
                print(f"   Remaining news rows after label filter: {len(news_data)}")
            # Balance data
            news_data = balance_data(news_data, "Nhãn/Label")
    else:
        print("📝 Using sample data...")
        news_data = pd.DataFrame(get_sample_news_data(), columns=['Nội Dung', 'Nhãn/Label'])

    # Append very high-confidence user feedback from DB (self-learning)
    user_news_df = load_user_feedback_data(PredictionType.NEWS, min_confidence=0.95)
    if user_news_df is not None and not user_news_df.empty:
        print(f"🔁 Augmenting news dataset with {len(user_news_df)} user-labelled samples.")
        news_data = pd.concat([news_data, user_news_df], ignore_index=True)
    
    # Map labels to indices dynamically based on labels present
    unique_labels = sorted(news_data["Nhãn/Label"].unique())
    label_map = {label: idx for idx, label in enumerate(unique_labels)}
    news_data['label'] = news_data['Nhãn/Label'].map(label_map)
    
    # Kiểm tra nhãn lỗi (typo / giá trị lạ → NaN)
    na_count = news_data['label'].isna().sum()
    if na_count > 0:
        print(f"🔴 Lỗi nhãn News: {na_count} dòng map ra NaN. Giá trị lạ: {news_data.loc[news_data['label'].isna(), 'Nhãn/Label'].unique().tolist()}")
        news_data = news_data.dropna(subset=['label'])
        if len(news_data) == 0:
            raise ValueError("Không còn dòng nào sau khi bỏ nhãn lỗi.")
        unique_labels = sorted(news_data["Nhãn/Label"].unique())
        label_map = {label: idx for idx, label in enumerate(unique_labels)}
        news_data['label'] = news_data['Nhãn/Label'].map(label_map)
    
    # Apply same preprocessing as inference (giống news_service.predict() → clean_text)
    X = news_data['Nội Dung'].apply(clean_text)
    y = news_data['label'].astype(int)
    
    print(f"\n📊 Final dataset:")
    print(f"   Total samples: {len(X)}")
    for label, idx in label_map.items():
        print(f"   {label}: {sum(y == idx)}")
    print(f"   Label distribution:\n{pd.Series(y).value_counts()}")
    
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
    
    # TF-IDF: min_df=1 tránh mất từ vựng; dataset nhỏ → ít feature, sublinear_tf=False
    n_samples = len(X_train)
    use_sublinear_tf = n_samples >= SMALL_DATASET_THRESHOLD
    max_feat = min(12000, max(1000, n_samples * 15))
    vectorizer = TfidfVectorizer(
        max_features=max_feat,
        ngram_range=(1, 3),
        stop_words=list(VIETNAMESE_STOPWORDS),
        sublinear_tf=use_sublinear_tf,
        min_df=1,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    if len(X_test) > 0:
        X_test_vec = vectorizer.transform(X_test)
    else:
        X_test_vec = None
    
    # Debug pipeline
    vocab_size = len(vectorizer.vocabulary_)
    print(f"\n🔍 Pipeline debug (News):")
    print(f"   Vocabulary size: {vocab_size}")
    if vocab_size < 50:
        print(f"   ⚠️  CẢNH BÁO: Vocabulary < 50 → model học rất yếu. Thêm dữ liệu hoặc kiểm tra min_df.")
    print(f"   X_train shape: {X_train_vec.shape}")
    print(f"   X_test shape: {X_test_vec.shape if X_test_vec is not None else 'N/A'}")
    print(f"   Label distribution (train):\n{pd.Series(y_train).value_counts()}")
    
    # Train và so sánh cả 2 model cho news: MultinomialNB vs Logistic Regression (Softmax)
    print("\n🤖 Training and comparing News models (MultinomialNB vs Logistic Regression)")
    news_models = {}
    
    # Naive Bayes (Multinomial) cho multi-class
    news_models["Naive Bayes"] = MultinomialNB(alpha=1.0)
    
    # Logistic Regression (Softmax)
    try:
        log_reg = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            multi_class='multinomial',
            class_weight='balanced',
            C=2.0,
        )
    except TypeError:
        # For newer sklearn versions without multi_class parameter
        log_reg = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            class_weight='balanced',
            C=2.0,
        )
    
    news_models["Logistic Regression"] = log_reg
    
    results = []
    print("\n📐 Softmax: P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)")
    
    for name, clf in news_models.items():
        print(f"\n--- {name} ---")
        clf.fit(X_train_vec, y_train)
        
        if X_test_vec is not None and len(y_test) > 0:
            y_pred = clf.predict(X_test_vec)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            print(f"Accuracy: {accuracy:.4f}")
            print(f"F1-Score (weighted): {f1:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            print("Confusion Matrix (rows=true, cols=pred):")
            print(cm)
            
            # Nhãn theo đúng index trong label_map
            unique_indices = sorted(pd.unique(y))
            idx_to_label = {idx: label for label, idx in label_map.items()}
            target_names = [idx_to_label[idx] for idx in unique_indices]
            
            # Confusion matrix heatmap
            cm_path = reports_dir / f"news_confusion_{name.lower().replace(' ', '_')}.png"
            plot_confusion_matrix(
                cm,
                class_names=target_names,
                title=f"News - {name}",
                save_path=cm_path,
            )
            
            # Cross Validation (5-fold nếu đủ dữ liệu)
            cv_acc = None
            if len(y_train) >= 5:
                scores = cross_val_score(clf, X_train_vec, y_train, cv=5)
                cv_acc = scores.mean()
                print(f"CV Accuracy (5-fold): {cv_acc:.4f}")
            else:
                print("⚠️  Not enough samples for 5-fold cross validation.")
            
            results.append(
                {
                    "Model": name,
                    "Accuracy": accuracy,
                    "F1": f1,
                    "CV_Accuracy": cv_acc,
                }
            )
            
            print("\n📋 Classification Report:")
            print(
                classification_report(
                    y_test,
                    y_pred,
                    labels=unique_indices,
                    target_names=target_names,
                )
            )
        else:
            print("⚠️  No test data available (dataset too small). Skipping evaluation and CV.")
    
    # Bảng so sánh tổng hợp
    if results:
        print("\n📊 News model comparison (hold-out + cross-validation):")
        header = f"{'Model':<20}{'Accuracy':<12}{'F1':<12}{'CV Accuracy':<12}"
        print(header)
        print("-" * len(header))
        model_names = []
        accuracies = []
        for r in results:
            cv_str = f"{r['CV_Accuracy']:.4f}" if r["CV_Accuracy"] is not None else "-"
            print(f"{r['Model']:<20}{r['Accuracy']:<12.4f}{r['F1']:<12.4f}{cv_str:<12}")
            model_names.append(r["Model"])
            accuracies.append(r["Accuracy"])
        
        # Biểu đồ so sánh Accuracy
        acc_path = reports_dir / "news_model_accuracy_comparison.png"
        plot_accuracy_comparison(
            model_names,
            accuracies,
            title="News Models Accuracy Comparison",
            save_path=acc_path,
        )
    else:
        print("\n⚠️  No evaluation results to compare (dataset too small).")
    # Chọn model deploy cuối cùng theo weighted F1 trên hold-out nếu có
    selected_news_model = "Logistic Regression"
    if results:
        selected_news_model = max(results, key=lambda r: r["F1"])["Model"]
        print(f"\n📐 Auto-selected best news model by weighted F1: {selected_news_model}.")
    model = news_models[selected_news_model]
    
    # Save model (attach label_map so inference knows dynamic labels)
    model_path = models_dir / "news_model.pkl"
    vectorizer_path = models_dir / "news_vectorizer.pkl"
    
    # Attach idx->label map for inference (API maps prediction index to label name)
    model.label_map = {idx: label for label, idx in label_map.items()}

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
    
    # Load base data from Excel / CSV if available
    data = None
    if USE_EXCEL and DATASET_PATH.exists():
        data = load_data_from_excel(DATASET_PATH)
    if USE_CSV and CSV_DATASET_PATH.exists():
        csv_data = load_data_from_csv(CSV_DATASET_PATH)
        if csv_data is not None:
            if data is None:
                data = csv_data
            else:
                print("🔗 Merging Excel + CSV training data")
                data = pd.concat([data, csv_data], ignore_index=True)
    
    # Train both models
    train_spam_model(data)
    train_news_model(data)
    
    print("\n✅ Training completed successfully!")
    print("\nYou can now start the API server.")
