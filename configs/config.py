import os
from typing import Literal

from configs.url_func import gen_mysql_db_url, gen_postgresql_db_url


class Config:
    """Configuration"""

    def __getitem__(self, key):
        return self.__getattribute__(key)

    HOST: str = "0.0.0.0"
    PORT: int = 8620
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    UVICORN_LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "WARNING"
    DATABASE_URL: str = ""
    JWT_SECRET_KEY: str = (
        os.getenv("JWT_SECRET_KEY") or f"secret:{os.urandom(32).hex()}"
    )
    JWT_REFRESH_SECRET_KEY: str = (
        os.getenv("JWT_REFRESH_SECRET_KEY") or f"refresh-secret:{os.urandom(32).hex()}"
    )
    SUPER_ACCESS_KEY: str = (
        os.getenv("SUPER_ACCESS_KEY") or f"super-access-key:{os.urandom(32).hex()}"
    )
    RELOAD: bool = False
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    ACCESS_QPM_LIMIT: int = 100


class DevConfig(Config):
    """Development environment configuration"""

    LOG_LEVEL = "DEBUG"
    UVICORN_LOG_LEVEL = "DEBUG"
    DATABASE_URL = gen_mysql_db_url(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "123456"),
        database="ng_presethub",
    )
    RELOAD = True
    DEBUG = True
    SUPER_ACCESS_KEY = "presethub-super-access-key"


class ProdConfig(Config):
    """Production environment configuration"""

    LOG_LEVEL = "WARNING"
    UVICORN_LOG_LEVEL = "WARNING"
    DATABASE_URL = gen_mysql_db_url(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "123456"),
        database="ng_presethub",
    )
    SUPER_ACCESS_KEY = os.getenv("SUPER_ACCESS_KEY")
    DEBUG = False
