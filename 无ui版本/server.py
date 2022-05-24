from cgitb import Hook
from socket import *
from utils import *
from struct import unpack
from threading import *
import tkinter as tk

dataBuf = {}
clients = {}

def workThread(dataBuf:bytes, conn:socket):
    global clients
    while 1:
        data = conn.recv(1024)
        if data:
            dataBuf += data
        while len(dataBuf) > HEADSIZE:
            header = unpack('!3i', dataBuf[:HEADSIZE])
            versionNum = header[0]
            msgType = header[1]
            bodyLen = header[2]
            if len(dataBuf) < HEADSIZE + bodyLen:
                break

            if msgType == HEART_BEAT_PACKAGE:
                conn.send(packData(HEART_BEAT_PACKAGE))
            elif msgType == MSG:
                newpackage = packData(MSG, clients[conn]+': '+dataBuf[HEADSIZE:HEADSIZE+bodyLen].decode('utf-8'))
                for client in clients:
                    if client != conn:
                        client.send(newpackage)
            elif msgType == LOG_IN:
                nickname = dataBuf[HEADSIZE:HEADSIZE+bodyLen].decode('utf-8')
                clients[conn] = nickname
                for client in clients:
                    if client != conn:
                        client.send(packData(MSG, nickname+' has entered'))
            else:
                print('default')
            dataBuf = dataBuf[HEADSIZE+bodyLen:]

if __name__ == '__main__':
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    while 1:
        conn, clientAddr = server.accept()
        print(clientAddr, ' has connected!')
        conn.send(packData(LOG_IN, 'welcome and input your nickname: '))
        clients[conn] = ''
        dataBuf[conn] = bytes()
        Thread(target=workThread, args=(dataBuf[conn], conn)).start()