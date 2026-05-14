"""
News Classification Service

Baseline: Softmax over TF-IDF features (logistic regression).

Extension: we also kiểm tra tỉ lệ từ khóa theo từng chủ đề:
- Với mỗi chủ đề tin tức, định nghĩa một bộ từ khóa tiêu biểu.
- Khi dự đoán:
  1. Làm sạch + tách token câu.
  2. Đếm bao nhiêu token thuộc bộ từ khóa của từng chủ đề.
  3. Tính phần trăm (ratio) của mỗi chủ đề trên tổng số token.
- Nếu model softmax tự tin thấp nhưng một chủ đề chiếm tỉ lệ từ khóa
  rõ ràng vượt trội, ta có thể dùng chủ đề đó làm quyết định cuối cùng.
"""
import pickle
import os
from pathlib import Path
from app.utils.preprocess import clean_text, tokenize

# Bộ từ khóa đơn giản cho từng chủ đề.
# Có thể mở rộng/tinh chỉnh thêm theo dữ liệu thực tế.
TOPIC_KEYWORDS = {
    "Thể thao": {
        "bóng", "bóng đá", "bóng rổ", "bàn thắng", "ghi bàn", "trận đấu",
        "cầu thủ", "huấn luyện viên", "chung kết", "giải đấu", "world cup",
        "olympic", "vđv", "vận động viên", "tỷ số", "bảng xếp hạng",
    },
    "Chính trị": {
        "quốc hội", "chính phủ", "nghị định", "thông tư", "bộ trưởng",
        "chủ tịch", "lãnh đạo", "bầu cử", "hiệp định", "ngoại giao",
        "chính sách", "đối ngoại", "ủy ban", "đại biểu", "hội nghị",
    },
    "Kinh tế": {
        "kinh tế", "gdp", "tăng trưởng", "lạm phát", "doanh nghiệp",
        "đầu tư", "chứng khoán", "thị trường", "cổ phiếu", "trái phiếu",
        "ngân hàng", "lãi suất", "xuất khẩu", "nhập khẩu", "doanh thu",
        "lợi nhuận", "thương mại", "tài chính",
    },
    "Công nghệ": {
        "công nghệ", "ai", "trí tuệ nhân tạo", "blockchain", "5g",
        "phần mềm", "phần cứng", "ứng dụng", "app", "máy tính",
        "điện thoại", "smartphone", "mạng xã hội", "internet", "cloud",
        "điện toán đám mây", "dữ liệu lớn", "big data", "startup",
    },
    "Giải trí": {
        "ca sĩ", "diễn viên", "bộ phim", "phim", "showbiz", "giải thưởng",
        "lễ hội", "âm nhạc", "bài hát", "album", "concert", "liveshow",
        "truyền hình", "gameshow", "nghệ sĩ", "ngôi sao",
    },
    "Y tế": {
        "y tế", "sức khỏe", "bệnh", "bệnh viện", "dịch", "cúm", "vaccine",
        "vắc xin", "khám", "điều trị", "bác sĩ", "thuốc", "tiêm phòng",
        "phòng bệnh", "virus", "sốt", "phẫu thuật", "đại dịch",
    },
}

class NewsClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._model_loaded = False
        # Default label map for older models; newer models will
        # provide their own dynamic label_map attached to the model.
        self.default_label_map = {
            0: "Thể thao",
            1: "Chính trị",
            2: "Kinh tế",
            3: "Công nghệ",
            4: "Giải trí",
            5: "Y tế"
        }
        self.label_map = self.default_label_map
        # Try to load model on init
        self._try_load_model()
    
    def _try_load_model(self):
        """Try to load the trained news classification model"""
        if self._model_loaded:
            return
        try:
            self.load_model()
            self._model_loaded = True
            print("News model loaded successfully")
        except FileNotFoundError as e:
            print(f"News model not found: {e}")
            self._model_loaded = False
        except Exception as e:
            print(f"Warning: Could not load news model: {e}")
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
            # Prefer dynamic label_map stored on the model (if present)
            model_label_map = getattr(self.model, "label_map", None)
            if isinstance(model_label_map, dict) and model_label_map:
                # Ensure keys are integers (class indices)
                self.label_map = {int(k): v for k, v in model_label_map.items()}
            else:
                self.label_map = self.default_label_map
            print(f"Loaded news model from: {model_path}")
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
                # Fallback: train once on demand so the app remains usable
                try:
                    from train_model import load_dataset, train_news

                    data = load_dataset()
                    train_news(data)
                    self._model_loaded = False
                    self._try_load_model()
                except Exception as train_err:
                    raise FileNotFoundError(
                        "News model not loaded. Please train the model first by running: python train_model.py"
                    ) from train_err
                if not self.model or not self.vectorizer:
                    raise FileNotFoundError(
                        "News model not loaded. Please train the model first by running: python train_model.py"
                    )
        
        # Step 1: Preprocess text
        cleaned_text = clean_text(text)
        tokens = tokenize(cleaned_text)

        # Phân tích từ khóa theo từng chủ đề
        topic_counts: dict[str, int] = {label: 0 for label in self.label_map.values()}
        # Allow heuristics to consider topics not present in the trained model.
        for extra_topic in TOPIC_KEYWORDS.keys():
            topic_counts.setdefault(extra_topic, 0)
        for token in tokens:
            for topic_label, keywords in TOPIC_KEYWORDS.items():
                if token in keywords:
                    topic_counts[topic_label] = topic_counts.get(topic_label, 0) + 1

        total_tokens = len(tokens) if tokens else 1
        topic_percentages: dict[str, float] = {
            topic_label: count / total_tokens
            for topic_label, count in topic_counts.items()
        }

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

        # Map prediction index to label name (dynamic label_map if available)
        ml_label = self.label_map.get(int(prediction), "Unknown")

        # Kết hợp softmax + heuristic dựa trên tỉ lệ từ khóa:
        # - Nếu model tự tin thấp
        # - Hoặc câu có tín hiệu chủ đề rất rõ (ví dụ "Bộ Y tế", "cúm mùa")
        #   → ưu tiên dùng chủ đề đó.
        final_label = ml_label
        final_confidence = confidence

        raw_text = (text or "").lower()
        strong_topic_overrides = [
            ("Y tế", ["bộ y tế", "sức khỏe", "cúm mùa", "tiêm phòng", "bệnh viện", "dịch bệnh", "vaccine", "vắc xin", "bác sĩ", "điều trị"]),
            ("Công nghệ", ["trí tuệ nhân tạo", "blockchain", "điện toán đám mây", "dữ liệu lớn", "startup", "phần mềm", "phần cứng", "5g"]),
            ("Thể thao", ["bóng đá", "bàn thắng", "trận đấu", "cầu thủ", "world cup", "olympic"]),
            ("Chính trị", ["quốc hội", "chính phủ", "bộ trưởng", "nghị định", "thông tư"]),
        ]
        for topic, phrases in strong_topic_overrides:
            if any(phrase in raw_text for phrase in phrases):
                final_label = topic
                final_confidence = max(confidence, 0.80)
                break

        if final_label == ml_label and topic_percentages:
            # Chủ đề có tỉ lệ từ khóa cao nhất
            keyword_topic, keyword_ratio = max(
                topic_percentages.items(), key=lambda kv: kv[1]
            )

            # Ngưỡng có thể chỉnh: tỉ lệ từ khóa & độ tự tin model
            LOW_CONF_THRESHOLD = 0.72     # softmax < 0.72 coi là chưa tự tin
            STRONG_TOPIC_RATIO = 0.18     # ≥18% token rơi vào 1 chủ đề

            if (
                keyword_ratio >= STRONG_TOPIC_RATIO
                and keyword_topic != ml_label
                and confidence < LOW_CONF_THRESHOLD
            ):
                final_label = keyword_topic
                # Dùng max(confidence, keyword_ratio) làm confidence xấp xỉ
                final_confidence = max(confidence, float(keyword_ratio))

        return {
            "label": final_label,
            "confidence": round(final_confidence, 4)
        }

# Global instance
news_classifier = NewsClassifier()
