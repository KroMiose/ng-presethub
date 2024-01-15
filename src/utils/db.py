from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.conf import config
from src.log import logger

# Create Database Connection:
Base = declarative_base()

# Init Database engine:
engine = create_engine(config.DATABASE_URL, pool_recycle=3600)
Base.metadata.create_all(engine)

connection = engine.connect()

def ensure_connection():
    global connection

    try:
        if connection.invalidated:
            connection.rollback()
            connection = engine.connect()
    except Exception as e:
        logger.error(f"Can not connect to database | Error: {e}")
        raise


logger.info(f"Connected to database {config.DATABASE_URL}")

# Create Database Session:
try:
    db: Session = sessionmaker(bind=engine)()
except:
    logger.exception("Failed to create DBSession")
    raise
