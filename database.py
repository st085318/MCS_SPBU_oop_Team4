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
        telegram_id INTEGER UNIQUE NOT NULL,
        first_name TEXT,
        second_name TEXT,
        clubs TEXT,
        description TEXT,
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
    sql = "INSERT INTO clients (telegram_id, first_name, second_name)\
          VALUES (?, ?, ?)"
    values = (telegram_id, first_name, second_name)
    cur.execute(sql, values)
    conn.commit()
    conn.close()


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


def show_clients():
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    print("CLIENTS :\n")
    for client in clients:
        print(client)
    cur.execute("SELECT * FROM clients_requests")
    clients = cur.fetchall()
    print("REQS :\n")
    for client in clients:
        print(client)


if __name__ == '__main__':
    create_db()
    conn = sqlite3.connect('club_to_everyone.db')
    cur = conn.cursor()
    show_clients()
    add_new_client(10, "AND", "YOU")
    show_clients()
    update_client_data(10, "CLUBS", "HOB")
    show_clients()