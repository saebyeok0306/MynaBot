from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHMY_DATABASE_URL = "sqlite:///db/mynaApp.db"
Base = declarative_base()
engine = create_engine(SQLALCHMY_DATABASE_URL)
# Base.metadata.bind = engine

Session = sessionmaker(bind=engine)


def init_db():
    import utils.database.model.users
    import utils.database.model.chats
    import utils.database.model.authority
    import utils.database.model.commands
    Base.metadata.create_all(engine)


class SessionContext:
    session = None

    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
