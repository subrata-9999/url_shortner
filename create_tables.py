# create_tables.py
from app.core.database import Base, engine
from app.models.url_models import URLBucket
from app.models.user_models import User
from app.models.record_models import Record

# Create tables in the database
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
