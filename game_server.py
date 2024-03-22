import socket
from _thread import *
import sys
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.0.100'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

currentId = "0"
pos = ["0:50,50:0:0", "1:100,100:0:0"]
points = [0, 0]

def threaded_client(conn):
    global currentId, pos, points
    conn.send(str.encode(currentId))
    currentId = "1"
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()

def collision_check():
    global pos, points
    blue_x, blue_y, _, _ = pos[0].split(":")
    red_x, red_y, _, _ = pos[1].split(":")
    if int(blue_x) == int(red_x) and int(blue_y) == int(red_y):
        points[1] += 1
        pos[0] = "0:50,50:0:0"
        pos[1] = "1:100,100:0:0"
        print("Collision detected! Red player gets a point.")

start_new_thread(collision_check, ())

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
