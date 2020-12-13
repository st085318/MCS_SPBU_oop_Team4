import sqlite3


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
            tags TEXT);
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clubs(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            club_name TEXT UNIQUE,
            description TEXT,
            tags TEXT);
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS requests(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            table_to_insert TEXT NOT NULL,
            club_telegram_id INTEGER,
            client_telegram_id INTEGER,
            new_value TEXT,
            action TEXT NOT NULL); 
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clubs_and_members(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            club_telegram_id INTEGER NOT NULL,
            member_telegram_id INTEGER NOT NULL,
            group_id INTEGER,
            condition INT NOT NULL
        );
        """)

        cur.execute("""CREATE TABLE IF NOT EXISTS clubs_groups(
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            club_telegram_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            timetable TEXT NOT NULL,
            description TEXT
        );
        """)


def is_user_client_or_club(telegram_id):
    # return None если пользователя нет
    #        1 если пользователь зарегистрирован как клуб
    #        2 если пользователь зарегистрирован как клиент
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM clients WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        is_user_client = cur.fetchone()

        sql = "SELECT * FROM clubs WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        is_user_club = cur.fetchone()
        if is_user_club:
            return 1
        if is_user_client:
            return 2
        return None


def add_new_client(telegram_id, client_name):
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
            sql = "INSERT INTO clients (telegram_id, first_name)\
                  VALUES (?, ?)"
            values = (telegram_id, client_name)
            cur.execute(sql, values)


def add_new_club(telegram_id, club_name):
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
        sql = "SELECT * FROM clubs WHERE club_name = (?)"
        cur.execute(sql, (club_name,))
        clubs_with_same_name = cur.fetchone()

        # Rewrite to make exception
        if clubs_with_same_name is not None:
            return 0

        elif exists_user is None:
            sql = "INSERT INTO clubs (telegram_id, club_name)\
              VALUES (?, ?)"
            values = (telegram_id, club_name)
            cur.execute(sql, values)
            return 1


def update_user_data(telegram_id, field_name, field_value, type_of_user):
    # type_of_user could be one of two values : club or client
    # может обновить любую ячейку в таблицах клиентов и клубов
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()

        sql = "INSERT INTO requests (table_to_insert, telegram_id, new_value, action)\
              VALUES (?, ?, ?, ?)"
        sql = sql.replace("telegram_id", type_of_user+"_telegram_id")
        values = (type_of_user+"s", telegram_id, field_value, "UPDATE " + field_name)
        cur.execute(sql, values)

        sql = "UPDATE type_of_user SET field_name = ? WHERE telegram_id = ?"
        sql = sql.replace("type_of_user", type_of_user+"s")
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
        value = (client_tg_id, )
        cur.execute(sql, value)
        first_name = cur.fetchall()
        sql = "SELECT second_name FROM clients WHERE telegram_id = ?"
        value = (client_tg_id, )
        cur.execute(sql, value)
        second_name = cur.fetchall()
        if second_name[0][0] is not None:
            return str(first_name[0][0]) + " " + str(second_name[0][0])
        return str(first_name[0][0])


def get_name_from_club_id(club_tg_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT club_name  FROM clubs WHERE telegram_id = ?"
        value = (club_tg_id, )
        cur.execute(sql, value)
        name = cur.fetchall()
        return name[0][0]


def get_club_id_from_club_name(club_name):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "SELECT telegram_id  FROM clubs WHERE club_name = ?"
        value = (club_name, )
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
        cur.execute(sql, (client_telegram_id, ))
        set_clubs_telegram_id = cur.fetchall()
        if not set_clubs_telegram_id:
            return None
        clubs_telegram_id = ""
        for club in set_clubs_telegram_id:
            clubs_telegram_id += str(club[0])+";"
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


def get_clubs_to_join():
    with sqlite3.connect('club_to_everyone.db') as conn:
        show_clubs()
        cur = conn.cursor()
        sql = "SELECT club_name FROM clubs WHERE telegram_id > 0"
        cur.execute(sql)
        clubs_names = cur.fetchall()
        sql = "SELECT description FROM clubs WHERE telegram_id > 0"
        cur.execute(sql)
        clubs_description = cur.fetchall()
        clubs = {}
        for i in range(0, len(clubs_names)):
            clubs.update({clubs_names[i][0]: clubs_description[i][0]})
        return clubs


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
=======

def create_db():
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS clients(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        second_name TEXT NOT NULL,
        clubs TEXT,
        hobbies TEXT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS host_clubs(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        club_name TEXT NOT NULL,
        description TEXT,
        members TEXT,
        tags TEXT);
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS clients_requests(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER NOT NULL,
        first_name TEXT,
        second_name TEXT,
        clubs TEXT,
        hobbies TEXT,
        tags TEXT,
        action TEXT NOT NULL); 
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS host_clubs_requests(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER NOT NULL,
        club_name TEXT,
        description TEXT,
        member TEXT,
        action TEXT NOT NULL);
    """)
    conn.commit()
    conn.close()


def add_new_client(telegram_id, first_name, second_name):
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    sql = "INSERT INTO clients_requests (telegram_id, first_name, second_name, action)\
          VALUES (?, ?, ?, ?)"
    values = (telegram_id, first_name, second_name, "CREATE")
    cur.execute(sql, values)
    sql = "SELECT * FROM clients WHERE telegram_user_id = ?"
    cur.execute(sql, telegram_id)
    exists_user = cur.fetchone()
    if exists_user is None:
        sql = "INSERT INTO clients (telegram_id, first_name, second_name)\
              VALUES (?, ?, ?)"
        values = (telegram_id, first_name, second_name)
        cur.execute(sql, values)
    conn.commit()
    conn.close()


# REWRITE
def update_client_data(telegram_id, clubs, hobbies):
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    sql = "INSERT INTO clients_requests (telegram_id, clubs, hobbies, action)\
          VALUES (?, ?, ?, ?)"
    values = (telegram_id, clubs, hobbies, "UPDATE")
    cur.execute(sql, values)
    sql = "UPDATE clients SET clubs = ?, hobbies = ? WHERE telegram_id = ?"
    values = (clubs, hobbies, telegram_id)
    cur.execute(sql, values)
    conn.commit()
    conn.close()


def add_new_club(telegram_id, club_name):
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    sql = "INSERT INTO host_clubs_requests (telegram_id, club_name, action)\
          VALUES (?, ?, ?)"
    values = (telegram_id, club_name, "CREATE")
    cur.execute(sql, values)
    sql = "SELECT * FROM host_clubs WHERE telegram_id = ?"
    values = (telegram_id, )
    cur.execute(sql, values)
    exists_user = cur.fetchone()
    if exists_user is None:
        sql = "INSERT INTO host_clubs (telegram_id, club_name)\
          VALUES (?, ?)"
        values = (telegram_id, club_name)
        cur.execute(sql, values)
    conn.commit()
    conn.close()


def update_description_of_club(telegram_id, description):
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    sql = "INSERT INTO host_clubs_requests (telegram_id, description, action)\
          VALUES (?, ?, ?)"
    values = (telegram_id, description, "ADDDESCR")
    cur.execute(sql, values)
    sql = "UPDATE host_clubs SET description = ? WHERE telegram_id = ?"
    values = (description, telegram_id)
    cur.execute(sql, values)
    conn.commit()
    conn.close()


def update_members_of_club(telegram_id, member_telegram_id):
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    sql = "INSERT INTO host_clubs_requests (telegram_id, member, action)\
          VALUES (?, ?, ?)"
    values = (telegram_id, member_telegram_id, "ADDMEMBER")
    cur.execute(sql, values)

    sql = "SELECT members FROM host_clubs WHERE telegram_id = ?"
    values = (telegram_id, )
    cur.execute(sql, values)
    members_of_club = cur.fetchone()
    members_of_club = members_of_club[0]
    if members_of_club is None:
        members_of_club = member_telegram_id
    else:
        members_of_club += ";" + member_telegram_id
    sql = "UPDATE host_clubs SET members = ? WHERE telegram_id = ?"
    values = (members_of_club, telegram_id)
    cur.execute(sql, values)
    conn.commit()
    conn.close()
