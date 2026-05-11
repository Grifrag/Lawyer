import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 3600        # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000    # 30 days
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = "Strict"
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://solon:devpassword@localhost:5432/solon")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-key-minimum-32-bytes!!")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-flask-secret-key")
    JWT_COOKIE_SECURE = False   # HTTP ok locally

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-minimum-32-bytes!!"
    SECRET_KEY = "test-flask-secret"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "")

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
