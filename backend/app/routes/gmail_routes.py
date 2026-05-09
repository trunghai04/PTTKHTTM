"""
Gmail scan: list emails, run spam classifier, save to predictions with source='gmail'.
Requires user to have linked Google (google_refresh_token).
"""
import base64
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Prediction, PredictionType
from app.auth.deps import get_current_user
from app.database.models import User
from app.services.spam_service import spam_classifier

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


def _credentials_from_refresh_token(refresh_token: str):
    from google.oauth2.credentials import Credentials
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )


def _get_message_body(payload: dict) -> str:
    """Extract body text from Gmail message payload."""
    if not payload:
        return ""
    # Prefer text/plain, but fall back to text/html if needed (bank receipts are often HTML only)
    if payload.get("body", {}).get("data"):
        try:
            data = payload["body"]["data"]
            return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="replace")
        except Exception:
            pass

    # Try parts
    preferred_part = None
    html_part = None
    for part in payload.get("parts", []):
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part.get("body", {}).get("data"):
            preferred_part = part
            break
        if mime == "text/html" and part.get("body", {}).get("data") and html_part is None:
            html_part = part

    target_part = preferred_part or html_part
    if target_part is not None:
        try:
            data = target_part["body"]["data"]
            return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="replace")
        except Exception:
            pass

    return ""


def _get_header(headers: list, name: str) -> str:
    if not headers:
        return ""
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "") or ""
    return ""


@router.post("/scan")
async def gmail_scan(
    max_messages: int = 200,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Scan user's Gmail inbox with spam classifier. Saves results to scan history.
    Requires Google account linked (login with Google first).
    """
    if not user.google_refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Chưa liên kết Gmail. Vui lòng đăng nhập bằng Google trước.",
        )
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Gmail scan chưa được cấu hình (thiếu GOOGLE_CLIENT_ID/SECRET).",
        )

    from google.auth.transport.requests import Request
    creds = _credentials_from_refresh_token(user.google_refresh_token)
    creds.refresh(Request())

    from googleapiclient.discovery import build
    service = build("gmail", "v1", credentials=creds)

    # Lấy nhiều email hơn bằng cách phân trang với nextPageToken.
    # max_messages: số email client yêu cầu;
    # hard_limit: giới hạn tuyệt đối để tránh quét quá nhiều.
    max_messages = max(1, max_messages or 50)
    hard_limit = 1000
    target = min(max_messages, hard_limit)

    messages: list[dict] = []
    fetched = 0
    page_token = None

    try:
        while fetched < target:
            page_size = min(100, target - fetched)
            resp = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=page_size,
                    pageToken=page_token,
                )
                .execute()
            )
            batch = resp.get("messages", []) or []
            if not batch:
                break
            messages.extend(batch)
            fetched += len(batch)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể lấy danh sách email: {str(e)}")

    scanned = 0
    spam_count = 0
    not_spam_count = 0

    for msg_ref in messages:
        try:
            msg = service.users().messages().get(userId="me", id=msg_ref["id"], format="full").execute()
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])
            subject = _get_header(headers, "Subject")
            snippet = (msg.get("snippet") or "")[:500]
            body = _get_message_body(payload) or snippet
            text = (subject + "\n\n" + body).strip() or snippet
            if not text:
                continue
        except Exception:
            continue

        try:
            res = spam_classifier.predict(text[:10000])
        except Exception:
            continue

        label = (res.get("label") or "").lower()
        if label == "spam":
            spam_count += 1
        else:
            not_spam_count += 1

        try:
            pred = Prediction(
                text=text[:5000],
                type=PredictionType.SPAM,
                predicted_label=res.get("label", "unknown"),
                confidence=float(res.get("confidence", 0)),
                user_id=user.id,
                source="gmail",
                email_subject=subject[:500] if subject else None,
                email_snippet=snippet[:300] if snippet else None,
            )
            db.add(pred)
            db.commit()
            scanned += 1
        except Exception:
            db.rollback()

    return {
        "scanned": scanned,
        "spam_count": spam_count,
        "not_spam_count": not_spam_count,
    }


@router.get("/history")
async def gmail_scan_history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current user's Gmail scan results (predictions with source=gmail)."""
    rows = (
        db.query(Prediction)
        .filter(Prediction.type == PredictionType.SPAM, Prediction.source == "gmail", Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [p.to_dict() for p in rows]
