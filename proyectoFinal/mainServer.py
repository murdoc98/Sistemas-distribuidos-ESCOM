import threading
import PySimpleGUI as sg
import json
import os
from socket import socket
from datetime import datetime
from random import randint
from dateutil import parser


server = socket()
server2 = socket()
server3= socket()
clientNo = 0
serverNo = 0
serverConnections = []
clientConnections = []
time = 0
serverService = False
clientService = False
books = [
    {'bookTitle': 'Introduccion to algorithms', 'url': './images/lib1.png'},
    {'bookTitle': 'Homo deus', 'url': './images/lib2.png'},
    {'bookTitle': 'The design of everiday things', 'url': './images/lib3.png'},
    {'bookTitle': 'Cracking the codding interview', 'url': './images/lib4.png'},
    {'bookTitle': 'Metro 2033', 'url': './images/lib5.png'}
]
url = ''

def resetServer():
    global clientConnections
    global books
    global clientNo
    for client in clientConnections:
        client.send('&'.encode())

def clientSync():
    global clientConnections
    for client in clientConnections:
        client.send(str(time).encode())

def serverSync():
    global serverConnections
    for server in serverConnections:
        servres = json.dumps(books)
        server.send(servres.encode())

def clockSocket(addr):
    global server3
    global time
    try:
        server3 = socket()
        server3.connect(addr)
        while True:
            data = server3.recv(1024).decode()
            if not data:
                raise Exception
            time = float(data)
            clientSync()
    except Exception as ex:
        print(ex)
        time = 0
        server3.close()

def clientPool(port):
    global server
    global clientNo
    global clientConnections
    server = socket()
    server.bind(('', port))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        clientConnections.append(conn)
        clientNo += 1
        t = threading.Thread(target=clientSocket, args=(conn, addr, ), name='client#{}'.format(clientNo))
        t.start()

def clientSocket(conn, addr):
    global clientNo
    global clientConnections
    global books
    global server2
    global url
    try:
        res = ''
        conn.send(str(time).encode())
        data = conn.recv(1024).decode()
        if data == '0':
            index = randint(0, len(books) - 1)
            res = books.pop(index)
            url = res['url']
            res = json.dumps(res)
            conn.send(res.encode())
            serverSync()
        data = conn.recv(1024).decode()
        if not data:
            raise Exception
    except Exception as ex:
        print(ex)
        clientConnections.remove(conn)
        clientNo -= 1
        if res != '':
            res = json.loads(res)
            books.append(res)
            serverSync()
        conn.close()

def serverPool(port):
    global serverNo
    server2 = socket()
    server2.bind(('', port))
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
        [sg.Text('Server hour: ', size=(20, 1), key='clock'), sg.InputText(key='utc_server', size=(13, 1)), sg.Button('Connect', size=(10, 1))],
        [sg.Text('Server Port:', size=(9, 1)), sg.InputText(key='server_port', size=(10, 1)), sg.Button('Serve', key='server_serve')],
        [sg.Text('Client Port:', size=(9, 1)), sg.InputText(key='client_port', size=(10, 1)), sg.Button('Serve', key='client_serve')],
        [sg.Text('Books left: 5', size=(100, 1),key='book', justification='center')],
        [sg.Text('Replicant servers: 0', size=(100, 1),key='replicants', justification='center')],
        [sg.Text('Users connected: 0', size=(100, 1),key='users', justification='center')],
        [sg.Button('Restart'), sg.Button('Print left books')],
        [sg.Text('Last choosen book'), sg.Image(filename='', key='image')]
    ]
    window = sg.Window('Main server', layout, size=(470,400), font='Helvetica 12')

    while True:
        event, values = window.read(timeout=10)
        window.Element('book').Update('Books left: {}'.format(len(books)))
        window.Element('replicants').Update('Replicant servers: {}'.format(serverNo))
        window.Element('users').Update('Users connected: {}'.format(clientNo))
        window.Element('image').Update(filename=url)
        if event == sg.WIN_CLOSED:
            server.close()
            break
        elif event == 'Print left books':
            print('Libros disponibles')
            for book in books:
                print(book['bookTitle'])
        elif event == 'Connect':
            if time == 0:
                utcIP = values['utc_server'][:values['utc_server'].find(':')]
                utcPORT = int(values['utc_server'][values['utc_server'].find(':') + 1:])
                addr = (utcIP, utcPORT)
                s = threading.Thread(target=clockSocket, args=(addr, ), name='clock')
                s.daemon = True
                s.start()
                window.Element('Connect').Update('Modify hour')
            else:
                print('Sincronizando clientes')
                data = values['utc_server']
                data = parser.parse(data).timestamp()
                time = data
                clientSync()
        elif event == 'server_serve':
            serverPort = int(values['server_port'])
            r = threading.Thread(target=serverPool, args=(serverPort, ), name='serverService')
            r.daemon = True
            r.start()
            serverService = True
        elif event == 'client_serve':
            clientPort = int(values['client_port'])
            t = threading.Thread(target=clientPool, args=(clientPort, ), name='clientService')
            t.daemon = True
            t.start()
            clientService = True
        elif event == 'Restart':
            resetServer()
            serverSync()

        if time == 0:
            window.Element('server_serve').Update(disabled=True)
            window.Element('client_serve').Update(disabled=True)
            window.Element('Restart').Update(disabled=True)
            window.Element('Print left books').Update(disabled=True)
        else:
            window.Element('server_serve').Update(disabled=False)
            window.Element('clock').Update('Server hour: {}'.format(str(datetime.fromtimestamp(time))[11:-4]))
            time += 0.01
            if serverService:
                window.Element('server_serve').Update(disabled=True)
                window.Element('client_serve').Update(disabled=False)
                window.Element('Restart').Update(disabled=False)
                window.Element('Print left books').Update(disabled=False)
                if clientService:
                    window.Element('client_serve').Update(disabled=True)

