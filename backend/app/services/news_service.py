"""
News Classification Service

Mathematical Implementation using Softmax:

Step 1: Calculate linear scores for each class
    z_j = w_j^T * x + b_j  (for j = 1 to 5)
    where:
    - w_j: weight vector for class j
    - x: TF-IDF feature vector
    - b_j: bias term for class j

Step 2: Apply Softmax function
    P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
    
    This normalizes scores to probabilities that sum to 1

Step 3: Predict class with highest probability
    y^ = argmax_j P(y=j|x)
"""
import pickle
import os
from pathlib import Path
from app.utils.preprocess import clean_text

class NewsClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._model_loaded = False
        self.label_map = {
            0: "Thể thao",
            1: "Chính trị",
            2: "Kinh tế",
            3: "Công nghệ",
            4: "Giải trí"
        }
        # Try to load model on init
        self._try_load_model()
    
    def _try_load_model(self):
        """Try to load the trained news classification model"""
        if self._model_loaded:
            return
        try:
            self.load_model()
            self._model_loaded = True
            print("✅ News model loaded successfully")
        except FileNotFoundError as e:
            print(f"⚠️  News model not found: {e}")
            self._model_loaded = False
        except Exception as e:
            print(f"⚠️  Warning: Could not load news model: {e}")
            self._model_loaded = False
    
    def load_model(self):
        """Load the trained news classification model"""
        # Try multiple paths
        base_path = Path(__file__).parent.parent
        possible_paths = [
            base_path / "models" / "news_model.pkl",
            base_path / "app" / "models" / "news_model.pkl",
            Path("app/models/news_model.pkl"),
            Path("backend/app/models/news_model.pkl"),
        ]
        
        model_path = None
        vectorizer_path = None
        
        for path in possible_paths:
            if path.exists():
                model_path = path
                vectorizer_path = path.parent / "news_vectorizer.pkl"
                break
        
        if model_path and model_path.exists() and vectorizer_path.exists():
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print(f"📦 Loaded news model from: {model_path}")
        else:
            raise FileNotFoundError(
                f"News model files not found. Searched in: {[str(p) for p in possible_paths]}. "
                "Please train the model first by running: python train_model.py"
            )
    
    def predict(self, text: str) -> dict:
        """
        Predict news category using Softmax
        
        Mathematical Process:
        1. Preprocess: Clean and normalize text
        2. Vectorize: Convert to TF-IDF feature vector x
        3. Calculate scores: z_j = w_j^T * x + b_j for each class j
        4. Apply Softmax: P(y=j|x) = e^(z_j) / Σ(k=1 to 5) e^(z_k)
        5. Predict: y^ = argmax_j P(y=j|x)
        
        Returns: {"label": category, "confidence": float}
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
                    "News model not loaded. Please train the model first by running: python train_model.py"
                )
        
        # Step 1: Preprocess text
        cleaned_text = clean_text(text)
        
        # Step 2: Vectorize using TF-IDF
        # Converts text to numerical feature vector x
        text_vector = self.vectorizer.transform([cleaned_text])
        
        # Step 3 & 4: Predict using Softmax
        # Internally computes:
        # - Linear scores: z_j = w_j^T * x + b_j
        # - Softmax probabilities: P(y=j|x) = e^(z_j) / Σe^(z_k)
        prediction = self.model.predict(text_vector)[0]
        probability = self.model.predict_proba(text_vector)[0]
        
        # Step 5: Get confidence (maximum probability from Softmax)
        # This is the probability of the predicted class
        confidence = float(max(probability))
        
        # Map prediction index to label name
        # 0: Thể thao, 1: Chính trị, 2: Kinh tế, 3: Công nghệ, 4: Giải trí
        label = self.label_map.get(prediction, "Unknown")
        
        return {
            "label": label,
            "confidence": round(confidence, 4)
        }

# Global instance
news_classifier = NewsClassifier()
