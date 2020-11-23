import sqlite3


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


