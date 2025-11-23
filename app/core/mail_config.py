from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,     # ✅ replaces old MAIL_TLS
    MAIL_SSL_TLS=False,     # ✅ replaces old MAIL_SSL
    USE_CREDENTIALS=True,
)
