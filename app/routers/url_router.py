from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.url_models import URLBucket, StatusEnum
from app.models.record_models import Record
from starlette.responses import RedirectResponse
from app.core.config import settings
import random
import string
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# take max request size from config
max_request_per_day = settings.MAX_REQUEST_SIZE

IST = ZoneInfo("Asia/Kolkata")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    original: str = None,
    short: str = None,
    exists: str = None,
    db: Session = Depends(get_db)
):

    username = request.session.get("username")
    email = request.session.get("email")
    user_id = int(request.session.get("user_id")) if request.session.get("user_id") else None

    # Device ID from cookie/header
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")

    short_url = None
    already_present = None

    if short:
        short_url = f"{settings.BASE_URL}/{short}"
        already_present = (exists == "1")

    # UNIVERSAL STATS
    stats = get_request_stats(db, user_id, device_id, max_request_per_day)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "email": email,
            "user_id": user_id,
            "device_id": device_id,
            "today_request_count": stats["today"],
            "pending_request_count": stats["pending"],
            "total_usage_count": stats["total"],
            "original_url": original,
            "short_url": short_url,
            "already_present": already_present,
            "max_request_per_day": max_request_per_day
        },
    )





@router.get("/{short_code}")
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    # Find the original URL
    url_entry = db.query(URLBucket).filter_by(short_url=short_code, status=StatusEnum.ACTIVE).first()
    if url_entry:
        return RedirectResponse(url_entry.original_url)
    return {"error": "Short URL not found or inactive"}


# ------------------ Helpers ------------------
def generate_short_code(length=6) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/shorten")
def shorten_url(
    request: Request,
    original_url: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = int(request.session.get("user_id")) if request.session.get("user_id") else None
    device_id = request.cookies.get("device_id") or request.headers.get("X-Device-ID")
    ip_address = request.client.host

    prevstats = get_request_stats(db, user_id, device_id, max_request_per_day)
    if prevstats["pending"] == 0:
        return JSONResponse(status_code=429, content={"status": "error", "message": "You have reached your daily limit. Please try again tomorrow."})

    # Check if URL exists
    existing = db.query(URLBucket).filter_by(original_url=original_url).first()

    if existing:
        short_code = existing.short_url
        short_url = f"{settings.BASE_URL}/{short_code}"
        trans_id = existing.id
    else:
        # Generate short code
        while True:
            short_code = generate_short_code()
            if not db.query(URLBucket).filter_by(short_url=short_code).first():
                break

        new_url = URLBucket(
            original_url=original_url,
            short_url=short_code,
            status=StatusEnum.ACTIVE
        )
        db.add(new_url)
        db.commit()
        db.refresh(new_url)

        short_url = f"{settings.BASE_URL}/{short_code}"
        trans_id = new_url.id

    # SAVE RECORD
    record = Record(
        trans_id=trans_id,
        user_id=user_id,
        device_id=device_id,
        ip_address=ip_address,
        created_at=datetime.now(IST)
    )
    db.add(record)
    db.commit()

    # Get updated stats
    stats = get_request_stats(db, user_id, device_id, max_request_per_day)

    return JSONResponse({
        "status": "success",
        "message": "URL shortened successfully!",
        "original_url": original_url,
        "short_url": short_url,
        "already_present": True if existing else False,
        "today_request_count": stats["today"],
        "pending_request_count": stats["pending"],
        "total_usage_count": stats["total"],
        "max_request_per_day": max_request_per_day
    })

    

def get_request_stats(db, user_id, device_id, max_limit):
    # Fix None values
    user_id = user_id if user_id else None
    device_id = device_id if device_id else None

    # IST date range
    now_ist = datetime.now(IST)
    today = now_ist.date()
    start_of_day = datetime.combine(today, datetime.min.time(), tzinfo=IST)
    end_of_day = datetime.combine(today, datetime.max.time(), tzinfo=IST)

    # Build OR filter logic
    base_filter = []
    if user_id:
        base_filter.append(Record.user_id == user_id)
    if device_id:
        base_filter.append(Record.device_id == device_id)

    # If both are None → return zero
    if not base_filter:
        return {
            "today": 0,
            "total": 0,
            "pending": max_limit
        }

    # Today count (OR logic)
    today_count = db.query(Record).filter(
        or_(*base_filter),
        Record.created_at >= start_of_day,
        Record.created_at <= end_of_day
    ).count()

    # Total lifetime count
    total_count = db.query(Record).filter(
        or_(*base_filter)
    ).count()

    # Pending today
    pending = max_limit - today_count

    return {
        "today": today_count,
        "total": total_count,
        "pending": pending
    }

