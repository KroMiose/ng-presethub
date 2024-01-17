from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.conf import config
from src.log import logger

# Create Database Connection:
Base = declarative_base()

# Init Database engine:
engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
Base.metadata.create_all(engine)


class connect_db:
    def __enter__(self):
        self.engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
        self.connection = self.engine.connect()
        if self.connection.invalidated:
            self.connection.rollback()
            self.connection = self.engine.connect()
        self.db: Session = sessionmaker(bind=self.engine)()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Error: {exc_type} | {exc_val} | {exc_tb}")
        else:
            self.db.close()


logger.info(f"Connected to database {config.DATABASE_URL}")

# Create Database Session:
try:
    with connect_db() as db:
        pass
except:
    logger.exception("Failed to create DBSession")
    raise
