from sqlalchemy.sql.sqltypes import *
from sqlalchemy.sql.schema import Column

from utils.database.Database import Base

import json


class Authoritys(Base):
    __tablename__ = "authority"

    id = Column(Integer, primary_key=True)
    roles = Column(String)

    def __init__(self, _id):
        self.id = _id
        self.roles = json.dumps([])

    def set_roles(self, _roles: list):
        self.roles = json.dumps(_roles)

    def get_roles(self):
        return json.loads(self.roles)
