# -*- coding: utf8 -*-
from sqlalchemy import Column, Integer, String, create_engine, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

engine = create_engine('sqlite:///test.db', echo=False)

Base = declarative_base()

# пользователь может быть клиентом или руководителем клуба
TypeOfUser = namedtuple('TypeOfUser', ['is_client', 'is_club', 'is_unknown'])

ClubInformation = namedtuple('ClubInformation', ['name', 'description', 'city'])


# класс с таблицей и методами клиентов
class Client(Base):
    __tablename__ = 'clients'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    client_name = Column(String, nullable=False)
    city = Column(String, nullable=False)

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
    def update_field(telegram_id: int, field_name: str, field_value: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).\
            filter(Client.telegram_id == telegram_id).first()
        if field_name == "client_name":
            client.name = field_value
        elif field_name == "city":
            client.city = field_value
        session.add(client)
        session.commit()


# класс с таблицей и методами клубов
class Club(Base):
    __tablename__ = 'clubs'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    club_name = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    description = Column(String)

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
            clubs.append(ClubInformation(club.club_name, club.description, club.city))
        return clubs

    @staticmethod
    def update_field(telegram_id: int, field_name: str, field_value: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        club = session.query(Club).\
            filter(Club.telegram_id == telegram_id).first()
        if field_name == "club_name":
            club.club_name = field_value
        elif field_name == "city":
            club.city = field_value
        elif field_name == "description":
            club.description = field_value
        session.add(club)
        session.commit()


# класс, помогающий отслеживать вступление и выход из клубов
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
    def get_id_members_of_club(club_telegram_id: int):
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


# класс, отвечающий за теги пользователей и клубов
class Tag(Base):
    __tablename__ = 'tags'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    science_tag = Column(Integer, nullable=False)
    sport_tag = Column(Integer, nullable=False)
    art_tag = Column(Integer, nullable=False)

    def __init__(self, telegram_id: int, art: int, science: int, sport: int):
        self.telegram_id = telegram_id
        self.art_tag = art
        self.science_tag = science
        self.sport_tag = sport

    @staticmethod
    def set_tags(telegram_id: int, sport: int, science: int, art: int):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(Tag).filter(Tag.telegram_id == telegram_id).first()
        if user is None:
            user = Tag(telegram_id, sport, science, art)
        else:
            user.sport_tag = sport
            user.science_tag = science
            user.art_tag = art
        session.add(user)
        session.commit()

    @staticmethod
    def add_tags(telegram_id: int, sport_add_value: int, science_add_value: int, art_add_value: int):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(Tag).filter(Tag.telegram_id == telegram_id).first()
        Tag.set_tags(telegram_id, user.sport_tag + sport_add_value, user.science_tag + science_add_value,
                     user.art_tag + art_add_value)

    @staticmethod
    def get_tags(telegram_id: int) -> dict:
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(Tag).filter(Tag.telegram_id == telegram_id).first()
        if user is None:
            user = Tag(telegram_id, 0, 0, 0)
        return {"art": user.art_tag, "sport": user.sport_tag, "science": user.science_tag}


def is_user_client_or_club(tg_id: int) -> TypeOfUser:
    Sess = sessionmaker(bind=engine)
    session = Sess()
    our_client = session.query(Client).filter_by(telegram_id=tg_id).all()
    our_club = session.query(Club).filter_by(telegram_id=tg_id).all()
    our_client = bool(our_client)
    our_club = bool(our_club)
    return TypeOfUser(our_client, our_club, not (our_client or our_club))


def create_db():
    Base.metadata.create_all(engine)
