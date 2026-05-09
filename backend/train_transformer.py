"""
Train a Vietnamese transformer-based classifier (e.g. PhoBERT/Vibert) on
the existing dataset (Excel + CSV).

This script is standalone and does NOT affect the existing TF‑IDF models.
It saves a HuggingFace model into app/transformer_model/.
"""

import os
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
import torch

from app.utils.preprocess import clean_text

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "app" / "transformer_model"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

EXCEL_PATH = BASE_DIR / "dataset.xlsx"
CSV_PATH = BASE_DIR / "dataset.csv"
MAX_TRAIN_SAMPLES = int(os.getenv("TRANSFORMER_MAX_TRAIN_SAMPLES", "2500"))


def load_combined_dataset() -> pd.DataFrame:
    frames: List[pd.DataFrame] = []

    if EXCEL_PATH.exists():
        df_x = pd.read_excel(EXCEL_PATH)
        if "Nội Dung" in df_x.columns and "Nhãn/Label" in df_x.columns:
            frames.append(df_x[["Nội Dung", "Nhãn/Label"]])

    if CSV_PATH.exists():
        # Skip bad lines (e.g. unescaped commas in content) so training can proceed
        try:
            df_c = pd.read_csv(CSV_PATH, engine="python", on_bad_lines="skip")
        except TypeError:
            # pandas < 2.0
            df_c = pd.read_csv(CSV_PATH, engine="python", error_bad_lines=False)
        # Normalise headers from CSV just like train_model.py
        if "Nội Dung" not in df_c.columns or "Nhãn/Label" not in df_c.columns:
            if "NoiDung" in df_c.columns:
                df_c = df_c.rename(columns={"NoiDung": "Nội Dung"})
            if "Label" in df_c.columns:
                df_c = df_c.rename(columns={"Label": "Nhãn/Label"})
        if "Nội Dung" in df_c.columns and "Nhãn/Label" in df_c.columns:
            frames.append(df_c[["Nội Dung", "Nhãn/Label"]])

    if not frames:
        raise RuntimeError("No valid dataset found in dataset.xlsx or dataset.csv")

    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["Nội Dung", "Nhãn/Label"])
    df["Nội Dung"] = df["Nội Dung"].astype(str)
    df["Nhãn/Label"] = df["Nhãn/Label"].astype(str).str.strip()

    # Focus on binary spam / not-spam for now.
    mask = df["Nhãn/Label"].isin(["Spam", "Not Spam"])
    df = df[mask].reset_index(drop=True)
    if df.empty:
        raise RuntimeError("No Spam / Not Spam rows found in dataset.")

    print(f"Loaded {len(df)} rows for Spam/Not Spam transformer training.")
    print(df["Nhãn/Label"].value_counts())
    return df


def main():
    df = load_combined_dataset()
    if MAX_TRAIN_SAMPLES > 0 and len(df) > MAX_TRAIN_SAMPLES:
        # Keep class balance while reducing CPU training time.
        df, _ = train_test_split(
            df,
            train_size=MAX_TRAIN_SAMPLES,
            random_state=42,
            stratify=df["Nhãn/Label"],
        )
        df = df.reset_index(drop=True)
        print(f"Using stratified subset: {len(df)} rows for transformer training.")

    df["text"] = df["Nội Dung"].apply(clean_text)
    label_encoder = LabelEncoder()
    df["label_id"] = label_encoder.fit_transform(df["Nhãn/Label"])

    train_df, eval_df = train_test_split(
        df[["text", "label_id"]], test_size=0.1, random_state=42, stratify=df["label_id"]
    )

    print(f"Train size: {len(train_df)}, Eval size: {len(eval_df)}")

    model_name = os.getenv("TRANSFORMER_MODEL_NAME", "distilbert-base-multilingual-cased")
    print(f"Using base transformer model: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_batch(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=256,
        )

    train_ds = Dataset.from_pandas(train_df.reset_index(drop=True))
    eval_ds = Dataset.from_pandas(eval_df.reset_index(drop=True))

    train_ds = train_ds.map(tokenize_batch, batched=True)
    eval_ds = eval_ds.map(tokenize_batch, batched=True)

    # HuggingFace expects these columns
    train_ds = train_ds.rename_column("label_id", "labels")
    eval_ds = eval_ds.rename_column("label_id", "labels")
    train_ds.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "labels"],
    )
    eval_ds.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "labels"],
    )

    num_labels = len(label_encoder.classes_)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=num_labels
    )

    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / "checkpoints"),
        num_train_epochs=float(os.getenv("TRANSFORMER_EPOCHS", "1")),
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        learning_rate=2e-5,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to=[],
    )

    def compute_metrics(eval_pred):
        from sklearn.metrics import accuracy_score, f1_score

        logits, labels = eval_pred
        preds = logits.argmax(axis=-1)
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average="weighted")
        return {"accuracy": acc, "f1": f1}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    print("Saving transformer model to", MODELS_DIR)
    model.save_pretrained(MODELS_DIR)
    tokenizer.save_pretrained(MODELS_DIR)

    # Save label mapping
    label_map_path = MODELS_DIR / "labels.txt"
    with label_map_path.open("w", encoding="utf-8") as f:
        for idx, name in enumerate(label_encoder.classes_):
            f.write(f"{idx}\t{name}\n")
    print("Label map saved to", label_map_path)


if __name__ == "__main__":
    main()

