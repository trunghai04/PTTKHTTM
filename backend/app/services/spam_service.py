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
            print("✅ Spam model loaded successfully")
        except FileNotFoundError as e:
            print(f"⚠️  Spam model not found: {e}")
            self._model_loaded = False
        except Exception as e:
            print(f"⚠️  Warning: Could not load spam model: {e}")
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
            print(f"📦 Loaded spam model from: {model_path}")
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
        
        # Get probabilities for each class
        # For binary: [P(Not Spam), P(Spam)] or [P(Spam), P(Not Spam)]
        # Check which index is Spam
        spam_prob = probability[1] if len(probability) > 1 else probability[0]
        not_spam_prob = probability[0] if len(probability) > 1 else (1 - probability[0])
        
        # Step 4: Apply threshold logic
        # Use threshold to reduce false positives
        # If spam_prob >= threshold AND spam_prob > not_spam_prob -> Spam
        # Otherwise -> Not Spam
        
        if spam_prob >= self.spam_threshold and spam_prob > not_spam_prob:
            label = "Spam"
            confidence = float(spam_prob)
        else:
            label = "Not Spam"
            confidence = float(not_spam_prob)
        
        # Warning for low confidence predictions
        if confidence < 0.7:
            print(f"⚠️  Low confidence prediction ({confidence:.2%}). Consider reviewing dataset quality.")
        
        return {
            "label": label,
            "confidence": round(confidence, 4),
            "spam_probability": round(float(spam_prob), 4),
            "not_spam_probability": round(float(not_spam_prob), 4)
        }

# Global instance with threshold
# Higher threshold (0.6-0.7) reduces false positives
# Lower threshold (0.5) is more sensitive but has more false positives
SPAM_THRESHOLD = 0.65  # Can be adjusted: 0.5 (sensitive) to 0.8 (strict)
spam_classifier = SpamClassifier(spam_threshold=SPAM_THRESHOLD)
