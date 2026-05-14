"""
Training script for Spam and News text classification.

This script:
- loads dataset.xlsx / dataset.csv
- trains a binary Spam classifier
- trains a multi-class News classifier for all non-spam labels
- saves models into app/models/
"""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import resample

from app.utils.preprocess import clean_text

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "app" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_XLSX = BASE_DIR / "dataset.xlsx"
DATASET_CSV = BASE_DIR / "dataset.csv"
CLEAN_XLSX = BASE_DIR / "dataset_clean.xlsx"
CLEAN_CSV = BASE_DIR / "dataset_clean.csv"
SPAM_LABELS = {"Spam", "Not Spam"}
LABEL_ALIASES = {
    "spam": "Spam",
    "not spam": "Not Spam",
    "notspam": "Not Spam",
    "not_spam": "Not Spam",
    "ham": "Not Spam",
    "1": "Spam",
    "0": "Not Spam",
}

STOPWORDS = {
    "và", "là", "của", "có", "được", "cho", "với", "trong", "này", "đó",
    "các", "một", "những", "đã", "sẽ", "khi", "như", "về", "từ", "đến",
    "hay", "hoặc", "nếu", "thì", "mà", "để", "bởi", "theo", "qua", "sau",
    "trước", "trên", "dưới", "ngoài", "giữa", "cùng", "vì", "do", "rằng",
}


def normalize_label(value: object) -> str:
    text = str(value).strip()
    key = text.lower().replace("_", " ").replace("-", " ")
    key = " ".join(key.split())
    return LABEL_ALIASES.get(key, text)


def load_dataset() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for path in (CLEAN_XLSX, CLEAN_CSV, DATASET_XLSX, DATASET_CSV):
        if not path.exists():
            continue
        if path.suffix.lower() == ".xlsx":
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path, engine="python", on_bad_lines="skip")

        rename_map = {}
        for col in df.columns:
            key = str(col).strip().lower().replace(" ", "").replace("_", "")
            if key in {"noidung", "content", "text"}:
                rename_map[col] = "Nội Dung"
            elif key in {"nhãn", "nhan", "label", "category", "nhãn/label", "nhan/label"}:
                rename_map[col] = "Nhãn/Label"
        if rename_map:
            df = df.rename(columns=rename_map)

        if {"Nội Dung", "Nhãn/Label"}.issubset(df.columns):
            df = df[["Nội Dung", "Nhãn/Label"]].copy()
            df = df.dropna(subset=["Nội Dung", "Nhãn/Label"])
            df["Nội Dung"] = df["Nội Dung"].astype(str).str.strip()
            df["Nhãn/Label"] = df["Nhãn/Label"].apply(normalize_label)
            df = df[(df["Nội Dung"] != "") & (df["Nhãn/Label"] != "")]
            frames.append(df)

    if not frames:
        raise FileNotFoundError("Không tìm thấy dataset.xlsx hoặc dataset.csv hợp lệ")

    data = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["Nội Dung"]).reset_index(drop=True)
    print(f"Loaded dataset: {len(data)} rows")
    print(data["Nhãn/Label"].value_counts().to_string())
    return data


def balance(df: pd.DataFrame, label_col: str = "Nhãn/Label") -> pd.DataFrame:
    max_count = df[label_col].value_counts().max()
    parts = []
    for _, group in df.groupby(label_col):
        parts.append(
            resample(
                group,
                replace=len(group) < max_count,
                n_samples=max_count,
                random_state=42,
            )
        )
    out = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    return out


def build_vectorizer(max_features: int, ngram_range: tuple[int, int]) -> TfidfVectorizer:
    return TfidfVectorizer(
        preprocessor=clean_text,
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=1,
        stop_words=list(STOPWORDS),
        sublinear_tf=True,
    )


def train_spam(data: pd.DataFrame) -> None:
    data = data.copy()
    data["Nhãn/Label"] = data["Nhãn/Label"].apply(normalize_label)

    spam = data[data["Nhãn/Label"].isin(["Spam", "Not Spam"])].copy()
    if spam.empty:
        raise ValueError("Không có dữ liệu Spam/Not Spam trong dataset")

    spam = balance(spam)
    X_train, X_test, y_train, y_test = train_test_split(
        spam["Nội Dung"], spam["Nhãn/Label"], test_size=0.2, random_state=42, stratify=spam["Nhãn/Label"],
    )

    vectorizer = build_vectorizer(max_features=6000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Naive Bayes": MultinomialNB(alpha=1.0),
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    }

    scored = []
    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        pred = model.predict(X_test_vec)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, pos_label="Spam")
        scored.append((name, model, acc, f1))
        print(f"[Spam] {name}: acc={acc:.4f}, f1={f1:.4f}")
        print(classification_report(y_test, pred))

    best_name, best_model, _, _ = max(scored, key=lambda x: x[3])
    print(f"[Spam] Selected model: {best_name}")

    with open(MODELS_DIR / "spam_model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    with open(MODELS_DIR / "spam_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)


def train_news(data: pd.DataFrame) -> None:
    data = data.copy()
    data["Nhãn/Label"] = data["Nhãn/Label"].apply(normalize_label)

    news = data[~data["Nhãn/Label"].isin(["Spam", "Not Spam"])].copy()
    if news.empty:
        raise ValueError("Không có dữ liệu news trong dataset")

    label_counts = news["Nhãn/Label"].value_counts()
    rare = label_counts[label_counts < 5].index.tolist()
    if rare:
        news = news[~news["Nhãn/Label"].isin(rare)].copy()
    news = balance(news)

    labels = sorted(news["Nhãn/Label"].unique())
    label_map = {label: idx for idx, label in enumerate(labels)}
    inv_map = {idx: label for label, idx in label_map.items()}
    y = news["Nhãn/Label"].map(label_map)

    X_train, X_test, y_train, y_test = train_test_split(
        news["Nội Dung"], y, test_size=0.2, random_state=42, stratify=y,
    )

    vectorizer = build_vectorizer(max_features=12000, ngram_range=(1, 3))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Naive Bayes": MultinomialNB(alpha=1.0),
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
    }

    scored = []
    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        pred = model.predict(X_test_vec)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, average="weighted")
        scored.append((name, model, acc, f1))
        print(f"[News] {name}: acc={acc:.4f}, f1={f1:.4f}")
        print(classification_report(y_test, pred, target_names=[inv_map[i] for i in sorted(inv_map)]))

    best_name, best_model, _, _ = max(scored, key=lambda x: x[3])
    print(f"[News] Selected model: {best_name}")
    best_model.label_map = inv_map

    with open(MODELS_DIR / "news_model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    with open(MODELS_DIR / "news_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)


def main() -> None:
    data = load_dataset()
    train_spam(data)
    train_news(data)
    print("Training completed successfully.")


if __name__ == "__main__":
    main()
