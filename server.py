import socket
import threading


def process_request(conn, addr):
    #print("connected client:", addr)
    ans = 0
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if data.decode("utf8") == "1":
                ans = 1


if __name__== "__main__":
    with socket.socket() as sock:
        sock.bind(("", 3085))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            th = threading.Thread(target=process_request, args=(conn, addr))
            th.start()
