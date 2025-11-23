from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
# from app.core.database import get_db
from app.core.database import SessionLocal
from app.models.user_models import User, UserStatus
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import secrets
from app.core.config import settings
from fastapi_mail import FastMail, MessageSchema
from app.core.mail_config import mail_conf
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from urllib.parse import unquote

import re

def validate_password(password: str):
    # Check bcrypt limit (72 bytes)
    if len(password.encode('utf-8')) > 72:
        return "Password too long — must be under 72 characters."

    # Basic security rules
    if len(password) < 8:
        return "Password too short — must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    return None  # ✅ means password is valid


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# password hasher
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ---------- FRONTEND ROUTES ---------- #

@router.get("/register", response_class=HTMLResponse)
def show_register_page(request: Request):
    if request.session.get("is_logged_in"):
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("register.html", {"request": request})


# @router.get("/login", response_class=HTMLResponse)
# def show_login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def show_login_page(request: Request, success: str = None, error: str = None):
    if request.session.get("is_logged_in"):
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "success": unquote(success) if success else None,
            "error": unquote(error) if error else None,
        },
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        # 🧠 check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Email already registered!"},
            )

        # 🔒 hash password
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # validate password
        validation_error = validate_password(password)
        if validation_error:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": f"⚠️ {validation_error}"},
            )

        # hash only after validation passes
        hashed_password = pwd_context.hash(password)



        # 🎟️ generate verification token
        verification_token = secrets.token_urlsafe(32)
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)

        # 🧑‍💻 create new user
        new_user = User(
            username=name,
            email=email,
            password_hash=hashed_password,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            verification_token=verification_token,
            verification_token_expires=token_expiry,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 📧 send email
        from app.core.mail_config import mail_conf
        from fastapi_mail import FastMail, MessageSchema

        verification_link = f"{settings.BASE_URL}/verify?token={verification_token}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; line-height:1.6;">
            <h2 style="color:#facc15;">Welcome, {name}!</h2>
            <p>Thanks for signing up for <b>URL Shortener</b>.</p>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verification_link}" 
               style="background:#facc15;color:black;padding:10px 20px;
                      border-radius:6px;text-decoration:none;font-weight:bold;">
                Verify Email
            </a>
            <p style="margin-top:20px;font-size:14px;color:#666;">
                This link expires in 24 hours.
            </p>
        </div>
        """

        message = MessageSchema(
            subject="Verify your account - URL Shortener",
            recipients=[email],
            body=html_content,
            subtype="html",
        )

        fm = FastMail(mail_conf)
        await fm.send_message(message)

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "success": "✅ Registration successful! Please check your email for verification link.",
            },
        )

    except Exception as e:
        import traceback
        print("❌ ERROR IN REGISTER ROUTE:")
        print(traceback.format_exc())

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": f"⚠️ Something went wrong: {str(e)}",
            },
        )


@router.get("/verify", response_class=HTMLResponse)
def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            url = "/login?error=Invalid+or+expired+verification+link"
            return RedirectResponse(url=url, status_code=303)

        if user.is_verified:
            url = "/login?success=Your+email+is+already+verified"
            return RedirectResponse(url=url, status_code=303)

        now = datetime.now(timezone.utc)
        expiry = user.verification_token_expires
        if expiry.tzinfo is None:  # 🧠 ensure same timezone type
            expiry = expiry.replace(tzinfo=timezone.utc)

        if expiry < now:
            url = "/login?error=Verification+link+has+expired"
            return RedirectResponse(url=url, status_code=303)

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()

        url = "/login?success=Your+email+has+been+verified+successfully"
        return RedirectResponse(url=url, status_code=303)

    except Exception as e:
        print("❌ VERIFY ERROR:", e)
        url = "/login?error=Something+went+wrong"
        return RedirectResponse(url=url, status_code=303)


@router.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.email == email).first()

        # if no user
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "❌ Invalid email or password"},
            )

        # if not verified yet
        if not user.is_verified:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "⚠️ Please verify your email before logging in."},
            )

        # if inactive
        if not user.is_active:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "🚫 Your account is inactive."},
            )

        # password check
        if not pwd_context.verify(password, user.password_hash):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "❌ Invalid email or password"},
            )

        # ✅ success → create session
        request.session["is_logged_in"] = True
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["email"] = user.email
        # ✅ success → redirect to home
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="user_email", value=user.email, httponly=True)
        return response

    except Exception as e:
        import traceback
        print("❌ LOGIN ERROR:", traceback.format_exc())
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"⚠️ Something went wrong: {str(e)}"},
        )

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login?success=Logged+out+successfully", status_code=303)
