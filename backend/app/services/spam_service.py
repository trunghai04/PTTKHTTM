"""
Spam Classification Service

Mathematical Implementation:

If using Naive Bayes:
    y^ = argmax_c P(c) * ∏(i=1 to n) P(w_i|c)
    - P(c): Prior probability of class c
    - P(w_i|c): Probability of word w_i given class c
    - Assumes conditional independence (Naive assumption)

If using Logistic Regression:
    P(y=1|x) = 1 / (1 + e^(-z))
    where z = w^T * x + b
    - w: weight vector
    - x: feature vector (TF-IDF)
    - b: bias term
    - Sigmoid function outputs probability between 0 and 1
"""
import pickle
import os
from pathlib import Path
from typing import List, Tuple

import math

from app.utils.preprocess import clean_text

class SpamClassifier:
    def __init__(self, spam_threshold=0.6):
        """
        Initialize spam classifier
        
        Args:
            spam_threshold: Minimum confidence to classify as Spam (default: 0.6)
                           Higher threshold = fewer false positives
        """
        self.model = None
        self.vectorizer = None
        self._model_loaded = False
        self.spam_threshold = spam_threshold  # Threshold for Spam classification
        # Try to load model on init
        self._try_load_model()
    
    def _try_load_model(self):
        """Try to load the trained spam classification model"""
        if self._model_loaded:
            return
        try:
            self.load_model()
            self._model_loaded = True
            print("Spam model loaded successfully")
        except FileNotFoundError as e:
            print(f"Spam model not found: {e}")
            self._model_loaded = False
        except Exception as e:
            print(f"Warning: Could not load spam model: {e}")
            self._model_loaded = False
    
    def load_model(self):
        """Load the trained spam classification model"""
        # Try multiple paths
        base_path = Path(__file__).parent.parent
        possible_paths = [
            base_path / "models" / "spam_model.pkl",
            base_path / "app" / "models" / "spam_model.pkl",
            Path("app/models/spam_model.pkl"),
            Path("backend/app/models/spam_model.pkl"),
        ]
        
        model_path = None
        vectorizer_path = None
        
        for path in possible_paths:
            if path.exists():
                model_path = path
                vectorizer_path = path.parent / "spam_vectorizer.pkl"
                break
        
        if model_path and model_path.exists() and vectorizer_path.exists():
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print(f"Loaded spam model from: {model_path}")
        else:
            raise FileNotFoundError(
                f"Spam model files not found. Searched in: {[str(p) for p in possible_paths]}. "
                "Please train the model first by running: python train_model.py"
            )
    
    def predict(self, text: str) -> dict:
        """
        Predict if text is spam or not spam
        
        Mathematical Process:
        1. Preprocess: Clean and normalize text
        2. Vectorize: Convert text to TF-IDF feature vector x
        3. Predict:
           - Naive Bayes: y^ = argmax_c P(c) * ∏P(w_i|c)
           - Logistic Regression: P(y=1|x) = sigmoid(w^T*x + b)
        4. Return: Class with highest probability
        
        Returns: {"label": "Spam" or "Not Spam", "confidence": float}
        """
        # Always try to load if not loaded
        if not self._model_loaded:
            self._try_load_model()
        
        # Double check and try again if still not loaded
        if not self.model or not self.vectorizer:
            # Try loading one more time
            self._try_load_model()
            if not self.model or not self.vectorizer:
                # Fallback: train once on demand so the app remains usable
                try:
                    from train_model import load_dataset, train_spam

                    data = load_dataset()
                    train_spam(data)
                    self._model_loaded = False
                    self._try_load_model()
                except Exception as train_err:
                    raise FileNotFoundError(
                        "Spam model not loaded. Please train the model first by running: python train_model.py"
                    ) from train_err
                if not self.model or not self.vectorizer:
                    raise FileNotFoundError(
                        "Spam model not loaded. Please train the model first by running: python train_model.py"
                    )
        
        # Step 1: Preprocess text
        cleaned_text = clean_text(text)
        
        # Step 2: Vectorize using TF-IDF
        # Converts text to numerical feature vector x
        text_vector = self.vectorizer.transform([cleaned_text])
        
        # Step 3: Predict using trained model
        # For Naive Bayes: Computes P(c|x) using Bayes theorem
        # For Logistic Regression: Computes P(y=1|x) using sigmoid
        probability = self.model.predict_proba(text_vector)[0]
        
        # Map probabilities by class label to avoid relying on class order.
        classes = list(getattr(self.model, "classes_", []))
        class_prob = {str(cls): float(probability[idx]) for idx, cls in enumerate(classes)}
        spam_prob = class_prob.get("Spam")
        not_spam_prob = class_prob.get("Not Spam")

        # Fallback for older models or unexpected class labels.
        if spam_prob is None or not_spam_prob is None:
            if len(probability) > 1:
                spam_prob = float(max(probability))
                not_spam_prob = float(min(probability))
            else:
                spam_prob = float(probability[0])
                not_spam_prob = float(1 - probability[0])
        
        # Step 4: Apply heuristic boost before thresholding.
        spam_prob, not_spam_prob, warning = self._phishing_boost(text, float(spam_prob), float(not_spam_prob))

        # Lower threshold = fewer false negatives for phishing/spam.
        if spam_prob >= self.spam_threshold and spam_prob > not_spam_prob:
            label = "Spam"
            confidence = float(spam_prob)
        else:
            label = "Not Spam"
            confidence = float(not_spam_prob)

        # Warning for low confidence predictions
        if confidence < 0.7:
            print(f"Low confidence prediction ({confidence:.2%}). Consider reviewing dataset quality.")
        
        result = {
            "label": label,
            "confidence": round(confidence, 4),
            "spam_probability": round(float(spam_prob), 4),
            "not_spam_probability": round(float(not_spam_prob), 4)
        }
        if warning:
            result["warning"] = warning
        return result

    def _phishing_boost(self, text: str, spam_prob: float, not_spam_prob: float) -> tuple[float, float, str | None]:
        """Lightweight heuristic boost for phishing-style messages."""
        raw = (text or "").lower()
        hits = 0
        for hint in ("xác minh", "tạm khóa", "bảo mật", "đăng nhập", "cập nhật", "khẩn cấp", "giao dịch", "thiết bị mới", "khôi phục", "xác thực", "bộ phận hỗ trợ", "vui lòng", "truy cập", "liên kết", "đường dẫn", "thông báo", "hạn chế"):
            if hint in raw:
                hits += 1
        has_url = any(u in raw for u in ("http://", "https://", "bit.ly", "tinyurl", "goo.gl", "t.co", "is.gd"))
        if hits >= 2 and has_url:
            spam_prob = max(spam_prob, 0.88)
            not_spam_prob = max(0.02, 1 - spam_prob)
            return spam_prob, not_spam_prob, "Phishing-style message detected: boosted spam score."
        if hits >= 4:
            spam_prob = max(spam_prob, 0.78)
            not_spam_prob = max(0.04, 1 - spam_prob)
            return spam_prob, not_spam_prob, "Suspicious security/account language detected."
        if has_url and ("tài khoản" in raw or "account" in raw or "mật khẩu" in raw or "password" in raw):
            spam_prob = max(spam_prob, 0.72)
            not_spam_prob = max(0.08, 1 - spam_prob)
            return spam_prob, not_spam_prob, "Account/security link detected."
        return spam_prob, not_spam_prob, None

    def predict_long(
        self,
        text: str,
        *,
        chunk_max_chars: int = 500,
        chunk_min_chars: int = 80,
    ) -> dict:
        """
        Predict for long texts by chunking then aggregating probabilities.

        Strategy:
        - Clean text once
        - Split into chunks (roughly) by max chars
        - Predict each chunk
        - Aggregate spam/not-spam probabilities weighted by chunk length
        """
        cleaned = clean_text(text)
        if len(cleaned) <= chunk_max_chars:
            return self.predict(text)

        chunks: List[str] = []
        buf: List[str] = []
        buf_len = 0
        for token in cleaned.split():
            if buf_len + len(token) + 1 > chunk_max_chars and buf_len >= chunk_min_chars:
                chunks.append(" ".join(buf))
                buf = [token]
                buf_len = len(token)
            else:
                buf.append(token)
                buf_len += len(token) + 1
        if buf:
            chunks.append(" ".join(buf))

        # Predict each chunk
        weighted_spam = 0.0
        weighted_not = 0.0
        total_w = 0.0

        for ch in chunks:
            out = self.predict(ch)
            w = max(1.0, float(len(ch)))
            total_w += w
            weighted_spam += w * float(out.get("spam_probability", 0.0))
            weighted_not += w * float(out.get("not_spam_probability", 0.0))

        if total_w <= 0:
            return self.predict(text)

        spam_prob = weighted_spam / total_w
        not_prob = weighted_not / total_w

        if spam_prob >= self.spam_threshold and spam_prob > not_prob:
            label = "Spam"
            confidence = spam_prob
        else:
            label = "Not Spam"
            confidence = not_prob

        return {
            "label": label,
            "confidence": round(float(confidence), 4),
            "spam_probability": round(float(spam_prob), 4),
            "not_spam_probability": round(float(not_prob), 4),
            "warning": "Long text: predicted via chunking + weighted aggregation.",
        }

# Global instance with threshold
# Higher threshold (0.8-0.9) strongly reduces false positives
# Lower threshold (0.5-0.6) is more sensitive but has more false positives
SPAM_THRESHOLD = 0.50  # aggressive: prioritize catching phishing-style spam
spam_classifier = SpamClassifier(spam_threshold=SPAM_THRESHOLD)
