from sqlalchemy import Column, Integer, String, create_engine, BOOLEAN, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

engine = create_engine('sqlite:///clients.db', echo=False)

Base = declarative_base()

# Пользователь может быть клиентом или руководителем клуба
TypeOfUser = namedtuple('TypeOfUser', ['is_client', 'is_club', 'is_unknown'])

ClubInformation = namedtuple('ClubInformation', ['name', 'description', 'city'])


# Класс с таблицей и методами клиентов
class Client(Base):
    __tablename__ = 'clients'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    client_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    location_latitude = Column(Float)
    location_longitude = Column(Float)

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
        session.commit()
        return client.city

    @staticmethod
    def get_name(telegram_id: int) -> str:
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).filter_by(telegram_id=telegram_id).first()
        session.commit()
        return client.client_name

    @staticmethod
    def get_location(tg_id: int) -> {}:
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).filter_by(telegram_id=tg_id).first()
        session.commit()
        return {'latitude': client.location_latitude, 'longitude': client.location_longitude}

    '''
    @staticmethod
    def get_talent(telegram_id: int) -> {}:
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).filter_by(telegram_id=telegram_id).first()
        return {'tech': client.talent_tech, 'art': client.talent_art, "humanitarian": client.talent_humanitarian,
                "physical": client.talent_physical}
    '''

    @staticmethod
    def update_field(telegram_id: int, field_name: str, field_value: str):
        Session = sessionmaker(bind=engine)
        session = Session()
        client = session.query(Client).\
            filter(Client.telegram_id == telegram_id).first()
        if field_name == "client_name":
            client.client_name = field_value
        elif field_name == "city":
            client.city = field_value
        elif field_name == "longitude":
            client.location_longitude = float(field_value)
        elif field_name == "latitude":
            client.location_latitude = float(field_value)
        session.add(client)
        session.commit()


# Класс с таблицей и методами клубов
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


# Класс, помогающий отслеживать вступление и выход из клубов
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


# Класс, отвечающий за теги пользователей и клубов
class Tag(Base):
    __tablename__ = 'tags'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    # Тэги - особые значения, отвечающие за направленность клуба
    tag_tech = Column(Integer, nullable=False)
    tag_humanitarian = Column(Integer, nullable=False)
    tag_art = Column(Integer, nullable=False)
    tag_sport = Column(Integer, nullable=False)
    tag_creative = Column(Integer, nullable=False)
    tag_artistic = Column(Integer, nullable=False)
    tag_literature = Column(Integer, nullable=False)

    def __init__(self, telegram_id: int, art: int, tech: int, sport: int, creative: int, artistic: int,
                 literature: int, humanitarian: int):
        self.telegram_id = telegram_id
        self.tag_art = art
        self.tag_tech = tech
        self.tag_sport = sport
        self.tag_creative = creative
        self.tag_artistic = artistic
        self.tag_literature = literature
        self.tag_humanitarian = humanitarian

    @staticmethod
    def set_tags(telegram_id: int, art: int, tech: int, sport: int, creative: int, artistic: int,
                 literature: int, humanitarian: int):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(Tag).get(telegram_id)
        if user is None:
            user = Tag(telegram_id, art, tech, sport, creative, artistic, literature, humanitarian)
        else:
            user.tag_sport = sport
            user.tag_art = art
            user.tag_tech = tech
            user.tag_creative = creative
            user.tag_artistic = artistic
            user.tag_literature = literature
            user.humanitarian = humanitarian
        session.add(user)
        session.commit()

    @staticmethod
    def add_tags(telegram_id: int, art_add_value: int, tech_add_value: int, sport_add_value: int,
                 creative_add_value: int,  artistic_add_value: int, literature_add_value: int,
                 humanitarian_add_value: int):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(Tag).get(telegram_id)
        Tag.set_tags(telegram_id, user.tag_art + art_add_value, user.tag_tech + tech_add_value,
                     user.tag_sport + sport_add_value, user.tag_creative + creative_add_value,
                     user.tag_artistic + artistic_add_value, user.tag_literature + literature_add_value,
                     user.tag_humanitarian + humanitarian_add_value)
        session.commit()

    @staticmethod
    def get_tags(telegram_id: int):
        tag_Session = sessionmaker(bind=engine)
        tag_session = tag_Session()
        user = tag_session.query(Tag).filter_by(telegram_id=telegram_id).first()
        if user is None:
            return {"art": 0, "sport": 0, "tech": 0, "creative": 0, "artistic": 0, "literature": 0,
                    "humanitarian": 0}
        return {"art": user.tag_art, "sport": user.tag_sport, "tech": user.tag_tech, "creative": user.tag_creative,
                "artistic": user.tag_artistic, "literature": user.tag_literature, "humanitarian": user.tag_humanitarian}


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
