from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column

from utils.database.Database import Base


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    boot_time = Column(String, nullable=True)
