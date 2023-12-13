from sqlalchemy import BLOB, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StashBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    ref = Column(String, index=True)


class StashMain(StashBase):
    __tablename__ = "stashMain"
    content = Column(BLOB)


class StashKeys(StashBase):
    __tablename__ = "stashKeys"
    content = Column(String)
