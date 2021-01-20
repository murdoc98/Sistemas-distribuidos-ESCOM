import threading
import PySimpleGUI as sg
import json
import os
from time import time as tm
from socket import socket
from datetime import datetime
from random import randint


server = socket()
server2 = socket()
server3= socket()
clientNo = 0
serverNo = 0
serverConnections = []
time = 0
books = [
    {'bookTitle': 'Introduccion to algorithms', 'url': '../images/lib1.jpg'},
    {'bookTitle': 'Homo deus', 'url': '../images/lib2.jpg'},
    {'bookTitle': 'The design of everiday things', 'url': '../images/lib3.jpg'},
    {'bookTitle': 'Cracking the codding interview', 'url': '../images/lib4.jpg'},
    {'bookTitle': 'Metro 2033', 'url': '../images/lib5.jpg'}
]

def broadcastSync():
    global serverConnections
    for server in serverConnections:
        servres = json.dumps(books)
        server.send(servres.encode())

def clockSocket():
    global server3
    global time
    try:
        server3.connect(('127.0.0.1', 8888))
        while True:
            data = server3.recv(1024).decode()
            if not data:
                raise Exception
            time = float(data)
    except Exception as ex:
        print(ex)
        server3.close()
        os._exit(1)

def clientPool():
    global server
    global clientNo
    server.bind(('', 8000))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        clientNo += 1
        t = threading.Thread(target=clientSocket, args=(conn, addr, ), name='client#{}'.format(clientNo))
        t.start()

def clientSocket(conn, addr):
    global clientNo
    global books
    global server2
    try:
        res = ''
        conn.send(str(time).encode())
        data = conn.recv(1024).decode()
        if data == '0':
            index = randint(0, len(books) - 1)
            res = json.dumps(books.pop(index))
            conn.send(res.encode())
            broadcastSync()
        data = conn.recv(1024).decode()
        if not data:
            raise Exception
    except Exception as ex:
        print(ex)
        clientNo -= 1
        if res != '':
            books.append(res)
            broadcastSync()
        conn.close()

def serverPool():
    global serverNo
    server2.bind(('', 8080))
    server2.listen(10)
    while True:
        conn, addr = server2.accept()
        serverNo += 1
        serverConnections.append(conn)
        t = threading.Thread(target=serverSocket, args=(conn, addr, ), name='server#{}'.format(serverNo))
        t.start()

def serverSocket(conn, addr):
    global serverNo
    global books
    try:
        serverNo += 1
        res = json.dumps(books)
        conn.send(res.encode())
        while True:
            data = conn.recv(1024).decode()
            if not data:
                raise Exception
            books = json.loads(data)
    except Exception as ex:
        print(ex)
        serverNo -= 1
        serverConnections.remove(conn)
        conn.close()

if __name__ == '__main__':
    sg.theme('DarkBlue16')
    layout = [
        [sg.Text('Server 1', size=(100, 1), justification='center')],
        [sg.Text('Server hour: ', size=(20, 1), key='clock'), sg.InputText(key='utc_server', size=(20, 1)), sg.Button('Connect')],
        [sg.Text('Port:'), sg.InputText(key='server_port', size=(10, 1)), sg.Button('Serve')],
        [sg.Text('Books left: 5', size=(100, 1),key='book', justification='center')],
        [sg.Text('Replicant servers: 0', size=(100, 1),key='replicants', justification='center')],
        [sg.Text('Users connected: 0', size=(100, 1),key='users', justification='center')],
        [sg.Button('Restart'), sg.Button('Print left books')],
    ]
    window = sg.Window('Main server', layout, size=(650,600), font='Helvetica 16')

    s = threading.Thread(target=clockSocket, args=(), name='clock')
    s.daemon = True
    s.start()

    r = threading.Thread(target=serverPool, args=(), name='server2')
    r.daemon = True
    r.start()

    t = threading.Thread(target=clientPool, args=(), name='server')
    t.daemon = True
    t.start()

    while True:
        event, values = window.read(timeout=10)
        window.Element('book').Update('Books left: {}'.format(len(books)))
        window.Element('replicants').Update('Replicant servers: 0'.format(serverNo))
        window.Element('users').Update('Users connected: {}'.format(clientNo))
        if event == sg.WIN_CLOSED:
            server.close()
            break
        elif event == 'Print left books':
            print('Libros disponibles')
            for book in books:
                print(book['bookTitle'])
        elif event == 'Serve':
            serverPoolPort = values['server_port']
            print(serverPoolPort)
            print('Servidor escuchando')
        if time != 0:
            window.Element('clock').Update('Server hour: {}'.format(str(datetime.fromtimestamp(time))[11:-4]))
            time += 0.01
