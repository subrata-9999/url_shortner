# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# # Change these to your XAMPP settings
# # DB_USER = "root"           # default XAMPP user
# # DB_PASSWORD = ""           # default is empty
# # DB_HOST = "127.0.0.1"      # or localhost
# # DB_NAME = "url_shortener"  # the database you just created

# DB_USER = "sql12809023"
# DB_PASSWORD = "DHg9dFsFix"
# DB_HOST = "sql12.freesqldatabase.com"
# DB_NAME = "sql12809023"

# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# engine = create_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()


# # app/core/database.py
# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool

# # load .env in local/dev
# load_dotenv()

# # Read DB values from single DATABASE_URL or components
# DATABASE_URL = os.getenv("DATABASE_URL")
# if not DATABASE_URL:
#     # fallback to components (if you prefer)
#     DB_USER = os.getenv("DB_USER", "sql12809023")
#     DB_PASSWORD = os.getenv("DB_PASSWORD", "")
#     DB_HOST = os.getenv("DB_HOST", "sql12.freesqldatabase.com")
#     DB_NAME = os.getenv("DB_NAME", "sql12809023")
#     DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# # For serverless, use NullPool and enable pool_pre_ping
# engine = create_engine(
#     DATABASE_URL,
#     echo=False,
#     pool_pre_ping=True,
#     poolclass=NullPool
# )

# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()


# app/core/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={
        "ssl": {
            "ca": "/var/task/app/core/ca.pem"
        }
    },
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()