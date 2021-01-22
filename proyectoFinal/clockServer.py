import PySimpleGUI as sg
import requests
import threading
from datetime import datetime
from socket import socket

server = socket()
serverNo = 0
serverConnections = []
def broadcastSync():
    global time
    global serverConnections
    for server in serverConnections:
        servres = str(time)
        server.send(servres.encode())

def serverPool():
    global serverNo
    global serverConnections
    server.bind(('', 8888))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        serverNo += 1
        serverConnections.append(conn)
        t = threading.Thread(target=serverSocket, args=(conn, addr, ), name='server#{}'.format(serverNo))
        t.start()

def serverSocket(conn, addr):
    global serverNo
    global serverConnections
    try:
        servres = str(time)
        conn.send(servres.encode())
        while True:
            data = conn.recv(1024).decode()
            if not data:
                raise Exception
    except Exception as ex:
        serverNo -= 1
        serverConnections.remove(conn)
        conn.close()

if __name__ == '__main__':
    response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC").json()
    time = response['unixtime']
    sg.theme('DarkBlue16')
    layout = [
        [sg.Text('UTC', size=(100, 0), key='title', justification='center')],
        [sg.Text('Servers connected: 0', size=(100, 0), key='connected', justification='center')],
        [sg.Text('Sync on 15', size=(100, 0), key='countdown', justification='center')],
        [sg.Text('', size=(100, 1), key='time', justification='center')],
    ]
    window = sg.Window('Clock server', layout, size=(230,120), font='Helvetica 12')
    counter = 20

    r = threading.Thread(target=serverPool, args=(), name='server2')
    r.daemon = True
    r.start()

    while True:
        event, values = window.read(timeout=10)
        strdate = str(datetime.fromtimestamp(time))[11:-4]
        window.Element('time').Update('Connected - {}'.format(strdate))
        window.Element('countdown').Update('Sync on {}'.format(int(counter)))
        window.Element('connected').Update('Servers connected {}'.format(serverNo))
        time += 0.01
        counter = round(counter - 0.01, 2)
        if counter == 0:
            broadcastSync()
            counter = 20
        if event == sg.WIN_CLOSED:
            break
