from socket import socket
from datetime import datetime
from random import randint
import os
import threading
import PySimpleGUI as sg
import json
from dateutil import parser

server = socket()
server2 = socket()
server3 = socket()
clientNo = 0
time = 0
books = []
booksBackup = []
serverService = False
clientService = False
clientConnections = []
url = ''
def clientSync():
    global clientConnections
    for client in clientConnections:
        client.send(str(time).encode())

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
        server3.close()

def clientPool(port):
    global server
    global clientNo
    global clientConnections
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
    global books
    global url
    global clientConnections
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
            servres = json.dumps(books)
            server2.send(servres.encode())
        data = conn.recv(1024).decode()
        if not data:
            raise Exception
    except:
        clientNo -= 1
        clientConnections.remove(conn)
        if res != '':
            books.append(res)
        conn.close()
        servres = json.dumps(books)
        server2.send(servres.encode())

def serverSocket(addr):
    global books
    try:
        server2.connect(addr)
        while True:
            data = server2.recv(1024).decode()
            if not data:
                raise Exception
            data = json.loads(data)
            books = data
    except Exception as ex:
        print(ex)
        server2.close()
        os._exit(1)

if __name__ == '__main__':
    sg.theme('DarkBlue16')
    layout = [
        [sg.Text('Rep server', size=(100, 1),justification='center')],
        [sg.Text('Server hour: ', size=(20, 1), key='clock'), sg.InputText(key='utc_server', size=(13, 1)), sg.Button('Connect', size=(10, 1), key='utc_connect')],
        [sg.Text('Main client:', size=(9, 1)), sg.InputText(key='main_server', size=(13, 1)), sg.Button('Connect', key='server_connect')],
        [sg.Text('Client Port:', size=(9, 1)), sg.InputText(key='client_port', size=(10, 1)), sg.Button('Serve', key='client_serve')],
        [sg.Text('Books left: 5', size=(100, 1),key='book', justification='center')],
        [sg.Text('Users connected: 0', size=(100, 1),key='status', justification='center')],
        [sg.Text('Direccion ip:'), sg.InputText(key='ip_port')],
        [sg.Button('Restart'), sg.Button('Print left books')],
        [sg.Text('Last choosen book'), sg.Image(filename='', key='image')]
    ]
    window = sg.Window('Replicant server', layout, size=(470,400), font='Helvetica 12')

    while True:
        event, values = window.read(timeout=10)
        window.Element('book').Update('Books left: {}'.format(len(books)))
        window.Element('status').Update('Users connected: {}'.format(clientNo))
        window.Element('image').Update(filename=url)
        if event == sg.WIN_CLOSED:
            server.close()
            break
        elif event == 'Print left books':
            for book in books:
                print(book['bookTitle'])
        elif event == 'utc_connect':
            if time == 0:
                utcIP = values['utc_server'][:values['utc_server'].find(':')]
                utcPORT = int(values['utc_server'][values['utc_server'].find(':') + 1:])
                addr = (utcIP, utcPORT)
                s = threading.Thread(target=clockSocket, args=(addr, ), name='clock')
                s.daemon = True
                s.start()
                window.Element('utc_connect').Update('Modify hour')
            else:
                print('Sincronizando clientes')
                data = values['utc_server']
                data = parser.parse(data).timestamp()
                time = data
                clientSync()
        elif event == 'server_connect':
            mainIP = values['main_server'][:values['main_server'].find(':')]
            mainPORT = int(values['main_server'][values['main_server'].find(':') + 1:])
            addr = (mainIP, mainPORT)
            r = threading.Thread(target=serverSocket, args=(addr, ), name='serverService')
            r.daemon = True
            r.start()
            serverService = True
        elif event == 'client_serve':
            clientPort = int(values['client_port'])
            t = threading.Thread(target=clientPool, args=(clientPort, ), name='clientService')
            t.daemon = True
            t.start()
            clientService = True
        
        if time == 0:
            window.Element('server_connect').Update(disabled=True)
            window.Element('client_serve').Update(disabled=True)
            window.Element('Restart').Update(disabled=True)
            window.Element('Print left books').Update(disabled=True)
        else:
            window.Element('server_connect').Update(disabled=False)
            window.Element('clock').Update('Server hour: {}'.format(str(datetime.fromtimestamp(time))[11:-4]))
            time += 0.01
            if serverService:
                window.Element('server_connect').Update(disabled=True)
                window.Element('client_serve').Update(disabled=False)
                window.Element('Restart').Update(disabled=False)
                window.Element('Print left books').Update(disabled=False)
                if clientService:
                    window.Element('client_serve').Update(disabled=True)