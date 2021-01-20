from socket import socket
from datetime import datetime
from random import randint
import os
import threading
import PySimpleGUI as sg
import json

server = socket()
server2 = socket()
clientNo = 0
time = datetime.timestamp(datetime.now())
books = []
def serverPool():
    global server
    global clientNo
    server.bind(('', 8002))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        clientNo += 1
        t = threading.Thread(target=clientSocket, args=(conn, addr, ), name='client#{}'.format(clientNo))
        t.start()

def clientSocket(conn, addr):
    global clientNo
    global books
    try:
        res = ''
        conn.send(str(time).encode())
        data = conn.recv(1024).decode()
        if data == '0':
            index = randint(0, len(books) -1)
            res = books.pop(index)
            res = json.dumps(res)
            conn.send(res.encode())
            servres = json.dumps(books)
            server2.send(servres.encode())
        data = conn.recv(1024).decode()
        if not data:
            raise Exception
    except:
        clientNo -= 1
        if res != '':
            books.append(res)
        conn.close()
        servres = json.dumps(books)
        server2.send(servres.encode())

def serverSocket():
    global books
    try:
        server2.connect(('', 8080))
        while True:
            data = server2.recv(1024).decode()
            if not data:
                raise Exception
            data = json.loads(data)
            print(data)
            books = data
    except Exception as ex:
        print(ex)
        server2.close()
        os._exit(1)

if __name__ == '__main__':
    sg.theme('DarkBlue16')
    layout = [
        [sg.Text('Server 2', size=(100, 1),justification='center')],
        [sg.Text('Server hour', size=(100, 1),key='clock', justification='center')],
        [sg.Text('Books left: 5', size=(100, 1),key='book', justification='center')],
        [sg.Text('Users connected: 0', size=(100, 1),key='status', justification='center')],
        [sg.Text('Direccion ip:'), sg.InputText(key='ip_port')],
        [sg.Button('Restart'), sg.Button('Print left books')],
    ]
    window = sg.Window('Replicant server', layout, size=(600,600), font='Helvetica 16')
    r = threading.Thread(target=serverSocket, args=(), name='server2')
    r.daemon = True
    r.start()

    t = threading.Thread(target=serverPool, args=(), name='server')
    t.daemon = True
    t.start()
    while True:
        event, values = window.read(timeout=10)
        time += 0.01
        window.Element('clock').Update('Server hour: {}'.format(str(datetime.fromtimestamp(time))[11:-4]))
        window.Element('book').Update('Books left: {}'.format(len(books)))
        window.Element('status').Update('Users connected: {}'.format(clientNo))
        if event == sg.WIN_CLOSED:
            server.close()
            break
        elif event == 'Print left books':
            for book in books:
                print(book['bookTitle'])