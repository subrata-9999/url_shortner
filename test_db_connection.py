from sqlalchemy import text
from app.core.database import engine

# Try to connect to MySQL
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))  # <-- wrap SQL in text()
        print("✅ Database connection successful!")
except Exception as e:
    print("❌ Database connection failed!")
    print("Error:", e)
