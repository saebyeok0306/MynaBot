from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint

from utils.database.Database import Base


class Exp(Base):
    __tablename__ = "exp"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, primary_key=True)
    chat_count = Column(Integer)
    cat_count = Column(Integer)
    today_str = Column(String)
    today_exp = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'guild_id'),
    )

    def __init__(self, _id, guild_id, chat_count=0, cat_count=0, today_str="", today_exp=0):
        self.id = _id
        self.guild_id = guild_id
        self.chat_count = chat_count
        self.cat_count = cat_count
        self.today_str = today_str
        self.today_exp = today_exp