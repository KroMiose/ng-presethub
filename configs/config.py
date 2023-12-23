import os
from typing import Literal
from urllib.parse import quote_plus


def gen_mysql_db_url(
    host: str = "localhost",
    port: int = 3306,
    user: str = "root",
    password: str = "",
    database: str = "",
    charset: str = "",
) -> str:
    """生成 MySQL 数据库连接 URL"""

    user = quote_plus(user)
    password = quote_plus(password)
    database = quote_plus(database)
    charset = quote_plus(charset)

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}{charset and f'?charset={charset}'}"


def gen_sqlite_db_url(db_path: str) -> str:
    """生成 SQLite 数据库连接 URL"""

    if not db_path.startswith("/") and not db_path.startswith("./"):
        db_path = f"./{db_path}"

    return f"sqlite:///{db_path}"


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
