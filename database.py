import sqlite3


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
            club_name TEXT,
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
            condition INT NOT NULL
        );
        """)


def add_new_client(telegram_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "INSERT INTO requests (table_to_insert, client_telegram_id, action)\
              VALUES (?, ?, ?)"
        values = ("clients", telegram_id, "CREATE")
        cur.execute(sql, values)
        sql = "SELECT * FROM clients WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        exists_user = cur.fetchone()
        if exists_user is None:
            sql = "INSERT INTO clients (telegram_id)\
                  VALUES (?)"
            values = (telegram_id, )
            cur.execute(sql, values)


def add_new_club(telegram_id):
    with sqlite3.connect('club_to_everyone.db') as conn:
        cur = conn.cursor()
        sql = "INSERT INTO requests (table_to_insert, club_telegram_id, action)\
              VALUES (?, ?, ?)"
        values = ("clubs", telegram_id, "CREATE")
        cur.execute(sql, values)
        sql = "SELECT * FROM clubs WHERE telegram_id = (?)"
        cur.execute(sql, (telegram_id,))
        exists_user = cur.fetchone()
        if exists_user is None:
            sql = "INSERT INTO clubs (telegram_id)\
              VALUES (?)"
            values = (telegram_id, )
            cur.execute(sql, values)


def update_user_data(telegram_id, field_name, field_value, type_of_user):
    # type_of_user could be one of two values : club or client
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


def get_clubs_of_client(client_telegram_id):
    pass


def get_members_of_club(club_telegram_id):
    pass


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
        cur.execute("SELECT * FROM host_clubs")
        clubs = cur.fetchall()
        print("CLUBS :\n")
        for club in clubs:
            print(club)
        cur.execute("SELECT * FROM host_clubs_requests")
        clubs = cur.fetchall()
        print("REQS :\n")
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
