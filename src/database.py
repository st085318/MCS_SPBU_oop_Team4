import sqlite3
from collections import namedtuple

# user - пользователь вообще
# client - тот, кто ищет кружок
# club - сама секция


def create_db():
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS clients(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            first_name TEXT,
            second_name TEXT,
            city TEXT,
            tag_sport INTEGER,
            tag_science INTEGER,
            tag_art INTEGER);
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clients_tags(
            id INTEGER AUTO_INCREMENT ,
            telegram_id INTEGER PRIMARY KEY,
            tag_sport INTEGER,
            tag_science INTEGER,
            tag_art INTEGER);
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clubs(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            club_name TEXT UNIQUE,
            city TEXT NOT NULL,
            description TEXT,
            tag_sport INTEGER,
            tag_science INTEGER,
            tag_art INTEGER);
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS requests(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            table_to_insert TEXT NOT NULL,
            club_telegram_id INTEGER,
            client_telegram_id INTEGER,
            new_value TEXT,
            action TEXT NOT NULL); 
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clubs_groups(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            club_telegram_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            timetable TEXT NOT NULL,
            description TEXT
        );
        """)


def set_tags(telegram_id: int, sport_value: int, science_value: int, art_value: int):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM clients_tags WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        exists_user = cur.fetchone()
        if exists_user is None:
            sql = "INSERT INTO clients_tags (telegram_id, tag_sport, tag_science, tag_art) VALUES (?, ?, ?, ?)"
            values = (telegram_id, sport_value, science_value, art_value)
            cur.execute(sql, values)

            sql = "SELECT * FROM clients_tags WHERE telegram_id = ?"
            values = (telegram_id, )
            cur.execute(sql, values)
            print(cur.fetchall())
        else:
            sql = "UPDATE clients_tags SET tag_sport = ? WHERE telegram_id = ?"
            values = (sport_value, telegram_id)
            cur.execute(sql, values)
            sql = "UPDATE clients_tags SET tag_science = ? WHERE telegram_id = ?"
            values = (science_value, telegram_id)
            cur.execute(sql, values)
            sql = "UPDATE clients_tags SET tag_art = ? WHERE telegram_id = ?"
            values = (art_value, telegram_id)
            cur.execute(sql, values)


def set_club_tags(telegram_id, sport_value, science_value, art_value):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = ("""INSERT or REPLACE INTO clubs(telegram_id, tag_sport, tag_science, tag_art)\
        VALUES (?, ?, ?, ?)""")
        values = (telegram_id, sport_value, science_value, art_value)
        cur.execute(sql, values)


def clear_tags(telegram_id: int):
    set_tags(telegram_id, 0, 0, 0)


def add_tags(telegram_id: int, sport_value: int, science_value: int, art_value: int):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        user_telegram_id = (telegram_id, )
        cur.execute('SELECT * FROM clients_tags WHERE telegram_id = ?', user_telegram_id)
        current_row = cur.fetchone()
        current_sport = current_row[2]
        current_science = current_row[3]
        current_art = current_row[4]
        set_tags(telegram_id, sport_value + current_sport, science_value + current_science, art_value + current_art)
        
        
def get_client_tags(telegram_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        tid = (telegram_id,)
        cur.execute('SELECT tag_sport FROM clients_tags WHERE telegram_id = ?', tid)
        current_sport = cur.fetchone()
        if current_sport is None:
            current_sport = 0
        cur.execute('SELECT tag_science FROM clients_tags WHERE telegram_id = ?', tid)
        current_science = cur.fetchone()
        if current_science is None:
            current_science = 0
        cur.execute('SELECT tag_art FROM clients_tags WHERE telegram_id = ?', tid)
        current_art = cur.fetchone()
        if current_art is None:
            current_art = 0

    return {"art": current_art, "sport": current_sport, "science": current_science}


TypeOfUser = namedtuple('TypeOfUser', ['is_client', 'is_club', 'is_unknown'])


def is_user_client_or_club(telegram_id: int) -> TypeOfUser:
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM clients WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        is_user_client = cur.fetchone()

        sql = "SELECT * FROM clubs WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        is_user_club = cur.fetchone()

        is_user_client = bool(is_user_client)
        is_user_club = bool(is_user_club)
        return TypeOfUser(is_user_client, is_user_club, not (is_user_client or is_user_club))


def add_new_client(telegram_id, client_name, client_city):
    # добавляет клиента, если он еще не зарегистрирован
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "INSERT INTO requests (table_to_insert, client_telegram_id, new_value, action)\
              VALUES (?, ?, ?, ?)"
        values = ("clients", telegram_id, client_name, "CREATE")
        cur.execute(sql, values)
        sql = "SELECT * FROM clients WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        exists_user = cur.fetchone()
        if exists_user is None:
            sql = "INSERT INTO clients (telegram_id, first_name, city)\
                  VALUES (?, ?, ?)"
            values = (telegram_id, client_name, client_city)
            cur.execute(sql, values)
            #sql = "INSERT INTO clients_tags (telegram_id, tag_sport, tag_science, tag_art)\
            #                  VALUES (?, ?, ?, ?)"
            #values = (telegram_id, 0, 0, 0)
            #cur.execute(sql, values)
    if exists_user is None:
        clear_tags(telegram_id)
        show_clients()


def add_new_club(telegram_id, club_name, club_city):
    # добавляет кружок, если он еще не зарегистрирован
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "INSERT INTO requests (table_to_insert, club_telegram_id, new_value, action)\
              VALUES (?, ?, ?, ?)"
        values = ("clubs", telegram_id, club_name, "CREATE")
        cur.execute(sql, values)
        sql = "SELECT * FROM clubs WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        exists_user = cur.fetchone()

        if exists_user is None:
            sql = "INSERT INTO clubs (telegram_id, club_name, city)\
              VALUES (?, ?, ?)"
            values = (telegram_id, club_name, club_city)
            cur.execute(sql, values)


def get_clients_city(telegram_id: int) -> str:
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT city FROM clients WHERE telegram_id = ?"
        value = (telegram_id,)
        cur.execute(sql, value)
        clients_city = cur.fetchall()
        return str(clients_city[0][0])


def update_user_data(telegram_id, field_name, field_value, type_of_user):
    # type_of_user could be one of two values : club or client
    # может обновить любую ячейку в таблицах клиентов и клубов
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()

        sql = "INSERT INTO requests (table_to_insert, telegram_id, new_value, action)\
              VALUES (?, ?, ?, ?)"
        sql = sql.replace("telegram_id", type_of_user + "_telegram_id")
        values = (type_of_user + "s", telegram_id, field_value, "UPDATE " + field_name)
        cur.execute(sql, values)

        sql = "UPDATE type_of_user SET field_name = ? WHERE telegram_id = ?"
        sql = sql.replace("type_of_user", type_of_user + "s")
        sql = sql.replace("field_name", field_name)
        values = (field_value, telegram_id)
        cur.execute(sql, values)


def add_member_to_club(club_telegram_id, member_telegram_id):
    # дописать return, для проверки записался ли человек в клуб или уже состоит
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()

        sql = "INSERT INTO requests (table_to_insert, club_telegram_id, client_telegram_id, action)\
              VALUES (?, ?, ?, ?)"
        values = ("clubs_and_members", club_telegram_id, member_telegram_id, "ADD MEMBER")
        cur.execute(sql, values)

        sql = "SELECT * FROM clubs_and_members WHERE club_telegram_id = ? AND member_telegram_id = ?"
        cur.execute(sql, (club_telegram_id, member_telegram_id))
        exists_member = cur.fetchone()

        if exists_member is None:
            sql = "INSERT INTO clubs_and_members (club_telegram_id, member_telegram_id, condition)\
                  VALUES (?, ?, ?)"
            values = (club_telegram_id, member_telegram_id, 1)
            cur.execute(sql, values)

        elif exists_member[1] == club_telegram_id and exists_member[2] == member_telegram_id and exists_member[3] == 0:
            sql = "UPDATE clubs_and_members SET condition = 1 WHERE club_telegram_id = ? AND member_telegram_id = ?"
            values = (club_telegram_id, member_telegram_id)
            cur.execute(sql, values)


def get_name_from_client_id(client_tg_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT first_name FROM clients WHERE telegram_id = ?"
        value = (client_tg_id,)
        cur.execute(sql, value)
        first_name = cur.fetchall()
        sql = "SELECT second_name FROM clients WHERE telegram_id = ?"
        value = (client_tg_id,)
        cur.execute(sql, value)
        second_name = cur.fetchall()
        if second_name[0][0] is not None:
            return str(first_name[0][0]) + " " + str(second_name[0][0])
        return str(first_name[0][0])


def get_name_from_club_id(club_tg_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT club_name  FROM clubs WHERE telegram_id = ?"
        value = (club_tg_id,)
        cur.execute(sql, value)
        name = cur.fetchall()
        return name[0][0]


def get_club_id_from_club_name(club_name):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT telegram_id  FROM clubs WHERE club_name = ?"
        value = (club_name,)
        cur.execute(sql, value)
        name = cur.fetchall()
        if not name:
            return None
        return name[0][0]


def out_member_from_club(club_telegram_id, member_telegram_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "INSERT INTO requests (table_to_insert, club_telegram_id, client_telegram_id, action)\
              VALUES (?, ?, ?, ?)"
        values = ("clubs_and_members", club_telegram_id, member_telegram_id, "MEMBER LEAVE")
        cur.execute(sql, values)

        sql = "SELECT * FROM clubs_and_members WHERE club_telegram_id = ? AND member_telegram_id = ?"
        cur.execute(sql, (club_telegram_id, member_telegram_id))
        exists_member = cur.fetchone()

        if exists_member is None:
            pass
        elif exists_member[1] == club_telegram_id and exists_member[2] == member_telegram_id and exists_member[3] == 1:
            sql = "UPDATE clubs_and_members SET condition = 0 WHERE club_telegram_id = ? AND member_telegram_id = ?"
            values = (club_telegram_id, member_telegram_id)
            cur.execute(sql, values)


def get_id_clubs_of_client(client_telegram_id):
    # получение telegram id клубов, в которые записан клиент
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT club_telegram_id FROM clubs_and_members WHERE member_telegram_id = ? AND condition = 1"
        cur.execute(sql, (client_telegram_id,))
        set_clubs_telegram_id = cur.fetchall()
        if not set_clubs_telegram_id:
            return None
        clubs_telegram_id = ""
        for club in set_clubs_telegram_id:
            clubs_telegram_id += str(club[0]) + ";"
        clubs_telegram_id = clubs_telegram_id[:-1]
        return clubs_telegram_id


def get_id_members_of_club(club_telegram_id):
    # перепесать, чтоб возвращал кортеж или тип того
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT member_telegram_id FROM clubs_and_members WHERE club_telegram_id = ? AND condition = 1"
        cur.execute(sql, (club_telegram_id,))
        set_members_telegram_id = cur.fetchall()
        if not set_members_telegram_id:
            return None
        members_telegram_id = ""
        for member in set_members_telegram_id:
            members_telegram_id += str(member[0]) + ";"
        members_telegram_id = members_telegram_id[:-1]
        return members_telegram_id


ClubInformation = namedtuple('ClubInformation', ['name', 'description', 'city'])


def get_clubs_to_join() -> [ClubInformation]:
    with sqlite3.connect('club_to_everyone.db') as conn:
        show_clubs()
        cur = conn.cursor()
        sql = "SELECT * FROM clubs"
        cur.execute(sql)
        clubs_info = cur.fetchall()
        clubs = []
        for club in clubs_info:
            clubs.append(ClubInformation(club[2], club[4], club[3]))
        return clubs


def show_tags():
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients_tags")
        row = cur.fetchall()
        print(row)


# functions show to debug
def show_clients():
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients")
        clients = cur.fetchall()
        print("CLIENTS :\n")
        for client in clients:
            print(client)
        cur.execute('SELECT * FROM requests WHERE table_to_insert LIKE ("clients")')
        clients = cur.fetchall()
        print("REQS :\n")
        for client in clients:
            print(client)


def show_clubs():
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clubs")
        clubs = cur.fetchall()
        print("CLUBS :\n")
        for club in clubs:
            print(club)


def show_members():
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clubs_and_members")
        clubs = cur.fetchall()
        print("CLUBS and their MEMS:\n")
        for club in clubs:
            print(club)

