"""
Script để phân tích dataset và đưa ra khuyến nghị
"""
import pandas as pd
from pathlib import Path
import os

DATASET_PATH = Path(__file__).parent / "dataset.xlsx"

def analyze_dataset():
    """Phân tích dataset và đưa ra khuyến nghị"""
    print("=" * 60)
    print("📊 Dataset Analysis")
    print("=" * 60)
    
    if not DATASET_PATH.exists():
        print(f"❌ Dataset not found: {DATASET_PATH}")
        return
    
    # Load data
    data = pd.read_excel(DATASET_PATH)
    data = data.dropna(subset=["Nội Dung", "Nhãn/Label"])
    data["Nhãn/Label"] = data["Nhãn/Label"].str.strip()
    
    # Filter spam data
    spam_labels = ["Spam", "Not Spam"]
    spam_data = data[data["Nhãn/Label"].isin(spam_labels)].copy()
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total rows: {len(data)}")
    print(f"   Spam-related rows: {len(spam_data)}")
    
    print(f"\n📊 Label Distribution (All):")
    label_counts = data["Nhãn/Label"].value_counts()
    for label, count in label_counts.items():
        percentage = (count / len(data)) * 100
        print(f"   {label:15s}: {count:4d} ({percentage:5.1f}%)")
    
    if len(spam_data) > 0:
        print(f"\n📧 Spam Classification Data:")
        spam_counts = spam_data["Nhãn/Label"].value_counts()
        total_spam = len(spam_data)
        
        for label, count in spam_counts.items():
            percentage = (count / total_spam) * 100
            print(f"   {label:15s}: {count:4d} ({percentage:5.1f}%)")
        
        # Check balance
        if "Spam" in spam_counts and "Not Spam" in spam_counts:
            spam_count = spam_counts["Spam"]
            not_spam_count = spam_counts["Not Spam"]
            ratio = spam_count / not_spam_count if not_spam_count > 0 else float('inf')
            
            print(f"\n⚖️  Balance Analysis:")
            print(f"   Spam / Not Spam ratio: {ratio:.2f}")
            
            if ratio < 0.5 or ratio > 2.0:
                print(f"   ⚠️  Dataset is IMBALANCED!")
                print(f"   Recommended ratio: 0.8 - 1.2")
            else:
                print(f"   ✅ Dataset is relatively balanced")
        
        # Check minimum samples
        min_samples = spam_counts.min()
        print(f"\n📉 Minimum samples per class: {min_samples}")
        
        if min_samples < 50:
            print(f"   ⚠️  WARNING: Too few samples!")
            print(f"   Recommended: At least 100-200 samples per class")
            print(f"   Current: Only {min_samples} samples")
        elif min_samples < 100:
            print(f"   ⚠️  Dataset is small but acceptable")
            print(f"   Recommended: 100+ samples per class for better accuracy")
        else:
            print(f"   ✅ Dataset size is good")
        
        # Analyze text length
        spam_data["text_length"] = spam_data["Nội Dung"].str.len()
        avg_length = spam_data["text_length"].mean()
        min_length = spam_data["text_length"].min()
        max_length = spam_data["text_length"].max()
        
        print(f"\n📏 Text Length Analysis:")
        print(f"   Average: {avg_length:.1f} characters")
        print(f"   Min: {min_length} characters")
        print(f"   Max: {max_length} characters")
        
        if avg_length < 50:
            print(f"   ⚠️  Texts are quite short - may affect accuracy")
        
        # Check for common spam words in Not Spam
        print(f"\n🔍 Quality Check:")
        not_spam_texts = spam_data[spam_data["Nhãn/Label"] == "Not Spam"]["Nội Dung"].str.lower()
        spam_texts = spam_data[spam_data["Nhãn/Label"] == "Spam"]["Nội Dung"].str.lower()
        
        spam_keywords = ["free", "won", "prize", "click", "urgent", "claim", "congratulations"]
        not_spam_keywords = ["email", "gửi", "thầy", "em", "xin", "cảm ơn", "vui lòng"]
        
        # Check if Not Spam contains spam keywords (potential mislabeling)
        mislabeled_count = 0
        for text in not_spam_texts:
            if any(keyword in text for keyword in spam_keywords):
                mislabeled_count += 1
        
        if mislabeled_count > 0:
            print(f"   ⚠️  Found {mislabeled_count} potential mislabeled Not Spam texts")
            print(f"      (Contains spam keywords but labeled as Not Spam)")
        
        # Recommendations
        print(f"\n" + "=" * 60)
        print("💡 Recommendations:")
        print("=" * 60)
        
        recommendations = []
        
        if min_samples < 100:
            recommendations.append(f"1. Increase dataset size to at least 100 samples per class")
            recommendations.append(f"   Current: {min_samples} samples, Target: 100+ samples")
        
        if "Spam" in spam_counts and "Not Spam" in spam_counts:
            spam_count = spam_counts["Spam"]
            not_spam_count = spam_counts["Not Spam"]
            if abs(spam_count - not_spam_count) > 20:
                recommendations.append(f"2. Balance the dataset")
                recommendations.append(f"   Spam: {spam_count}, Not Spam: {not_spam_count}")
                recommendations.append(f"   Target: Similar counts for both classes")
        
        if mislabeled_count > 0:
            recommendations.append(f"3. Review and fix mislabeled data")
            recommendations.append(f"   Found {mislabeled_count} potential mislabeled samples")
        
        if avg_length < 50:
            recommendations.append(f"4. Add longer text samples")
            recommendations.append(f"   Current avg: {avg_length:.0f} chars, Target: 50+ chars")
        
        recommendations.append(f"5. Add more Vietnamese academic/formal emails to Not Spam")
        recommendations.append(f"   Examples: 'Em gửi email đăng ký môn học', 'Thầy xem giúp em'")
        
        if not recommendations:
            print("   ✅ Dataset looks good! No major issues found.")
        else:
            for rec in recommendations:
                print(f"   {rec}")
        
        print(f"\n📝 Example Not Spam texts to add:")
        print(f"   - 'Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với.'")
        print(f"   - 'Thầy cho em hỏi về deadline nộp bài tập ạ.'")
        print(f"   - 'Em xin cảm ơn thầy đã phản hồi email của em.'")
        print(f"   - 'Em muốn đăng ký học phần này, thầy có thể hướng dẫn em không ạ?'")
        print(f"   - 'Em gửi file báo cáo như thầy yêu cầu, thầy xem giúp em ạ.'")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_dataset()
