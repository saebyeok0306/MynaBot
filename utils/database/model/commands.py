from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column

from utils.database.Database import Base

import json


class Commands(Base):
    __tablename__ = "command"

    guild_id = Column(Integer, primary_key=True)
    roles = Column(String)

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.roles = json.dumps([])

    def set_roles(self, _roles: list):
        self.roles = json.dumps(_roles)

    def get_roles(self):
        return json.loads(self.roles)
