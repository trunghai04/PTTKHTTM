"""
Script để test models có hoạt động không
"""
import sys
from pathlib import Path

print("=" * 60)
print("🧪 Testing Models")
print("=" * 60)

# Test 1: Kiểm tra models tồn tại
print("\n1️⃣ Checking model files...")
models_dir = Path("app/models")
if not models_dir.exists():
    print(f"❌ Models directory not found: {models_dir}")
    sys.exit(1)

required_files = [
    "spam_model.pkl",
    "spam_vectorizer.pkl",
    "news_model.pkl",
    "news_vectorizer.pkl"
]

missing_files = []
for file in required_files:
    file_path = models_dir / file
    if file_path.exists():
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - NOT FOUND")
        missing_files.append(file)

if missing_files:
    print(f"\n❌ Missing files: {missing_files}")
    print("   Run: python train_model.py")
    sys.exit(1)

# Test 2: Test import và load
print("\n2️⃣ Testing model loading...")
try:
    from app.services.spam_service import spam_classifier
    print(f"   ✅ Spam classifier imported")
    print(f"   ✅ Spam model loaded: {spam_classifier._model_loaded}")
    print(f"   ✅ Spam model exists: {spam_classifier.model is not None}")
    print(f"   ✅ Spam vectorizer exists: {spam_classifier.vectorizer is not None}")
except Exception as e:
    print(f"   ❌ Error loading spam classifier: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.services.news_service import news_classifier
    print(f"   ✅ News classifier imported")
    print(f"   ✅ News model loaded: {news_classifier._model_loaded}")
    print(f"   ✅ News model exists: {news_classifier.model is not None}")
    print(f"   ✅ News vectorizer exists: {news_classifier.vectorizer is not None}")
except Exception as e:
    print(f"   ❌ Error loading news classifier: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test prediction
print("\n3️⃣ Testing predictions...")
try:
    spam_result = spam_classifier.predict("You won a free iPhone!")
    print(f"   ✅ Spam prediction: {spam_result}")
except Exception as e:
    print(f"   ❌ Spam prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    news_result = news_classifier.predict("Messi ghi bàn trong trận chung kết")
    print(f"   ✅ News prediction: {news_result}")
except Exception as e:
    print(f"   ❌ News prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test API import
print("\n4️⃣ Testing API import...")
try:
    from app.main import app
    print(f"   ✅ FastAPI app imported")
except Exception as e:
    print(f"   ❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Models are ready to use.")
print("=" * 60)
print("\n🚀 You can now start the server:")
print("   uvicorn app.main:app --reload")
