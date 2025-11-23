from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

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

message = MessageSchema(
    subject="FastAPI-Mail Test",
    recipients=["subrataparam7@gmail.com"],
    body="<h3>Mail configuration works ✅</h3>",
    subtype="html",
)

fm = FastMail(mail_conf)
print("✅ import success — ready to send mail")
