from pathlib import Path
from typing import Optional

from app.utils.preprocess import clean_text


class TransformerSpamClassifier:
    """
    Lightweight wrapper around a fine-tuned transformer model for Spam/Not Spam.

    Expects a model directory (default: app/transformer_model) containing:
    - config + model weights
    - tokenizer files
    - labels.txt  (id<TAB>label)
    """

    def __init__(self, model_dir: Optional[Path] = None):
        base_dir = Path(__file__).parent.parent
        self.model_dir = model_dir or (base_dir / "transformer_model")

        self._loaded = False
        self.tokenizer = None
        self.model = None
        self._torch = None
        self._load_error: Optional[str] = None
        self.id2label: dict[int, str] = {}

    def _load(self):
        if self._loaded:
            return
        if self._load_error:
            raise RuntimeError(self._load_error)

        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Transformer model not found at {self.model_dir}. "
                "Please train it first with: python train_transformer.py"
            )

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
        except ModuleNotFoundError as e:
            self._load_error = (
                f"Transformer runtime is not installed ({e}). "
                "Install required packages and retry."
            )
            raise RuntimeError(self._load_error) from e

        self._torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
        self.model.eval()

        labels_path = self.model_dir / "labels.txt"
        if labels_path.exists():
            with labels_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    idx_str, name = line.split("\t", 1)
                    self.id2label[int(idx_str)] = name

        if not self.id2label:
            # Fallback mapping if label file is missing
            self.id2label = {0: "Not Spam", 1: "Spam"}

        self._loaded = True

    def predict(self, text: str) -> dict:
        """
        Run transformer-based Spam/Not Spam classification.
        Returns: {"label": str, "confidence": float}
        """
        self._load()

        cleaned = clean_text(text or "")
        inputs = self.tokenizer(
            cleaned,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )

        with self._torch.no_grad():
            outputs = self.model(**inputs)
            probs = self._torch.softmax(outputs.logits, dim=-1)[0]
            conf, idx = self._torch.max(probs, dim=-1)
        label = self.id2label.get(int(idx), str(int(idx)))

        return {
            "label": label,
            "confidence": float(conf),
            "spam_probability": float(probs[self._label_to_idx("Spam")] if "Spam" in self.id2label.values() else conf),
            "not_spam_probability": float(
                probs[self._label_to_idx("Not Spam")] if "Not Spam" in self.id2label.values() else (1.0 - conf)
            ),
        }

    def _label_to_idx(self, name: str) -> int:
        for i, n in self.id2label.items():
            if n == name:
                return i
        return 0


# Global instance
transformer_spam_classifier = TransformerSpamClassifier()

