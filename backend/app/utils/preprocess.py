import re
import string
import html
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and preprocess text for classification
    """
    if not isinstance(text, str):
        text = str(text or "")

    # Decode HTML entities and remove HTML tags (bill / email HTML body)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)

    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep Vietnamese characters
    text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize(text: str) -> List[str]:
    """
    Simple tokenization
    """
    return text.split()
