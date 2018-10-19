#!/usr/bin/env python3
import socket, threading

host = '192.168.1.4'
port = 51000 # random number

a = True

def reader(s):
    while a:
        mess = s.recv()
        print(mess) 


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

threading.Thread(target=reader, args=(s,)).start()

b = input()

while (b != '0'):
    s.send(bytes(b, 'utf-8'))
    b = input()

a = False

s.close()