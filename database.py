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
        tags TEXT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS clients_requests(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        club_name TEXT,
        description TEXT,
        tags TEXT,
        action TEXT NOT NULL     
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS host_clubs_requests(
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        first_name TEXT,
        second_name TEXT,
        clubs TEXT,
        hobbies TEXT,
        action TEXT NOT NULL);
    """)
    conn.commit()
    conn.close()


