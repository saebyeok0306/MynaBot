from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint

from utils.database.Database import Base


class Users(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    voice_type = Column(String, default="MALE")

    __table_args__ = (
        PrimaryKeyConstraint('id', 'guild_id'),
    )

    def __init__(self, _id, guild_id, username, voice_type="MALE"):
        self.id = _id
        self.guild_id = guild_id
        self.username = username
        self.voice_type = voice_type
