# replace bcrypt with argon2
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


try:
    hash_val = pwd_context.hash("Subrata@345")
    print("✅ Works! Hash:", hash_val)
except Exception as e:
    print("❌ Error:", e)
