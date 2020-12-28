from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

engine = create_engine('sqlite:///test.db', echo=False)

Base = declarative_base()

TypeOfUser = namedtuple('TypeOfUser', ['is_client', 'is_club', 'is_unknown'])

ClubInformation = namedtuple('ClubInformation', ['name', 'description', 'city', 'art_tag',\
                                                 'science_tag', 'sport_tag'])


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

    @staticmethod
    def add_new_client(telegram_id: int, name: str, city: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        new_client = Client(telegram_id, name, city)
        session.add(new_client)
        session.commit()

    # ?maybe one method
    @staticmethod
    def get_city(telegram_id: int) -> str:
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).filter_by(telegram_id=telegram_id).first()
        return client.city

    @staticmethod
    def get_name(telegram_id: int) -> str:
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).filter_by(telegram_id=telegram_id).first()
        return client.client_name

    @staticmethod
    def update_field(telegram_id: int, field_name: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).\
            filter(Client.telegram_id == telegram_id).first()
        if field_name == 0:
            membership.condition = 1

        session.add(membership)
        session.commit()

class Club(Base):
    __tablename__ = 'clubs'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    club_name = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    description = Column(String)
    art_tag = Column(Integer)
    science_tag = Column(Integer)
    sport_tag = Column(Integer)

    def __init__(self, telegram_id: int, name: str, city: str):
        self.telegram_id = telegram_id
        self.club_name = name
        self.city = city

    @staticmethod
    def add_new_club(telegram_id: int, name: str, city: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        new_club = Club(telegram_id, name, city)
        session.add(new_club)
        session.commit()

    @staticmethod
    def get_name_from_id(telegram_id: int) -> str:
        Session = sessionmaker(bind=engine)
        session = Session()
        club = session.query(Club).filter_by(telegram_id=telegram_id).first()
        return club.club_name

    @staticmethod
    def get_id_from_name(club_name: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        club = session.query(Club).filter_by(club_name=club_name).first()
        if not club:
            return None
        return club.telegram_id

    @staticmethod
    def get_clubs_to_join() -> [ClubInformation]:
        Session = sessionmaker(bind=engine)
        session = Session()
        clubs_objects = session.query(Club)
        clubs = []
        for club in clubs_objects:
            clubs.append(ClubInformation(club.club_name, club.description, club.city,
                                         club.art_tag, club.science_tag, club.sport_tag))
        return clubs


class Membership(Base):
    __tablename__ = "membership"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_telegram_id = Column(Integer, nullable=False)
    club_telegram_id = Column(Integer, nullable=False)
    condition = Column(BOOLEAN, nullable=False)

    def __init__(self, client_tg_id: int, club_tg_id: int):
        self.client_telegram_id = client_tg_id
        self.club_telegram_id = club_tg_id
        self.condition = 1

    @staticmethod
    def add_member_to_club(club_tg_id: int, client_tg_id: int):
        Sess = sessionmaker(bind=engine)
        session = Sess()
        membership = session.query(Membership).\
            filter(Membership.club_telegram_id == club_tg_id).filter(Membership.client_telegram_id == client_tg_id)\
            .first()
        if membership is None:
            new_membership = Membership(client_tg_id, club_tg_id)
            session.add(new_membership)
            session.commit()
        elif membership.condition == 0:
            membership.condition = 1
            session.add(membership)
            session.commit()

    @staticmethod
    def out_member_from_club(club_tg_id: int, client_tg_id: int):
        Sess = sessionmaker(bind=engine)
        session = Sess()
        membership = session.query(Membership). \
            filter(Membership.club_telegram_id == club_tg_id).filter(Membership.client_telegram_id == client_tg_id) \
            .first()
        if membership is None:
            pass
        elif membership.condition == 1:
            membership.condition = 0
            session.add(membership)
            session.commit()

    @staticmethod
    def get_id_members_of_club(club_telegram_id: int) -> str:
        Sess = sessionmaker(bind=engine)
        session = Sess()
        memberships = session.query(Membership).\
            filter(Membership.club_telegram_id == club_telegram_id).filter(Membership.condition == 1).all()
        if not memberships:
            return None
        members_telegram_id = ""
        for membership in memberships:
            members_telegram_id += str(membership.client_telegram_id) + ";"
        members_telegram_id = members_telegram_id[:-1]
        return members_telegram_id

    @staticmethod
    def get_id_clubs_of_client(client_telegram_id: int):
        Sess = sessionmaker(bind=engine)
        session = Sess()
        memberships = session.query(Membership).\
            filter(Membership.client_telegram_id == client_telegram_id).filter(Membership.condition == 1).all()
        if not memberships:
            return None
        clubs_telegram_id = ""
        for membership in memberships:
            clubs_telegram_id += str(membership.club_telegram_id) + ";"
        clubs_telegram_id = clubs_telegram_id[:-1]
        return clubs_telegram_id


def is_user_client_or_club(tg_id: int) -> TypeOfUser:
    Sess = sessionmaker(bind=engine)
    session = Sess()
    our_client = session.query(Client).filter_by(telegram_id=tg_id).all()
    our_club = session.query(Club).filter_by(telegram_id=tg_id).all()
    our_client = bool(our_client)
    our_club = bool(our_club)
    return TypeOfUser(our_client, our_club, not (our_client or our_club))


if __name__ == "__main__":
    Base.metadata.create_all(engine)
