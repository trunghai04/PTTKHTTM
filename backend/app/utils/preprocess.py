import re
import string
import html
from typing import List

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


def _strip_html(text: str) -> str:
    """Extract visible text from HTML email/bill bodies."""
    if not text:
        return ""

    if BeautifulSoup is not None and ("<" in text and ">" in text):
        try:
            soup = BeautifulSoup(text, "html.parser")
            # Remove script/style/noscript blocks before extracting text
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(" ", strip=True)
        except Exception:
            pass
    else:
        text = re.sub(r"<[^>]+>", " ", text)

    return text


def clean_text(text: str) -> str:
    """
    Clean and preprocess text for classification
    """
    if not isinstance(text, str):
        text = str(text or "")

    # Decode HTML entities and remove HTML markup (bill / email HTML body)
    text = html.unescape(text)
    text = _strip_html(text)

    # Convert to lowercase
    text = text.lower()

    # Remove common email boilerplate / tracking noise
    boilerplate_patterns = [
        r"unsubscribe",
        r"view in browser",
        r"open in browser",
        r"privacy policy",
        r"terms of service",
        r"if you cannot view this email",
        r"this email was sent to",
        r"please do not reply",
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    
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
