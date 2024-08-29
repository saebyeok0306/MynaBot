from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint

from utils.database.Database import Base


class Chats(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, primary_key=True)
    history = Column(String, nullable=True)
    data = Column(String, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'guild_id'),
    )

    def __init__(self, _id, guild_id, history, data):
        self.id = _id
        self.guild_id = guild_id
        self.history = history
        self.data = data
