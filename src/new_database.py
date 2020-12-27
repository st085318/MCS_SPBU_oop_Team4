from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

engine = create_engine('sqlite:///test.db', echo=False)

Base = declarative_base()

TypeOfUser = namedtuple('TypeOfUser', ['is_client', 'is_club', 'is_unknown'])


class Client(Base):
    __tablename__ = 'clients'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    client_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    tag_sport = Column(Integer)
    tag_science = Column(Integer)
    tag_art = Column(Integer)

    def __init__(self, telegram_id: int, name: str, city: str):
        self.telegram_id = telegram_id
        self.client_name = name
        self.city = city


class Club(Base):
    __tablename__ = 'clubs'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    club_name = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    description = Column(String)
    minor_tag = Column(Integer)

    def __init__(self, telegram_id, name, city, minor_tag):
        self.telegram_id = telegram_id
        self.client_name = name
        self.city = city
        self.minor_tag = minor_tag


def is_user_client_or_club(tg_id: int) -> TypeOfUser:
    Sess = sessionmaker(bind=engine)
    session = Sess()
    our_client = session.query(Client).filter_by(telegram_id=tg_id).all()
    our_club = session.query(Club).filter_by(telegram_id=tg_id).all()
    our_client = bool(our_client)
    our_club = bool(our_club)
    return TypeOfUser(our_client, our_club, not(our_client or our_club))


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    check_us = Client(21, "What", "city")
    Sess = sessionmaker(bind=engine)
    session = Sess()
    session.add(check_us)
    session.commit()