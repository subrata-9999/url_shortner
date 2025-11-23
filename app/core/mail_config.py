from fastapi_mail import ConnectionConfig

mail_conf = ConnectionConfig(
    MAIL_USERNAME="subrataapramanik46@gmail.com",
    MAIL_PASSWORD="ivxoplbeklwbwsfy",
    MAIL_FROM="subrataapramanik46@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,     # ✅ replaces old MAIL_TLS
    MAIL_SSL_TLS=False,     # ✅ replaces old MAIL_SSL
    USE_CREDENTIALS=True,
)
