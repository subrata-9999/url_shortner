class Settings:
    BASE_URL: str = "http://localhost:8000"
    # e.g., MAX_URL_REQUESTS = 10
    #       SECRET_KEY = "random_secret_key"
    MAX_REQUEST_SIZE: int = 10

settings = Settings()
