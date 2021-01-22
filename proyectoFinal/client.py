import PySimpleGUI as sg
import threading
from datetime import datetime
from socket import socket
import json
state = False
s = socket()
time = 0
book = ''
def clientSocket(addr):
    global state
    global time
    global book
    global url
    try:
        s = socket()
        s.connect(addr)
        #reqTime = datetime.now().timestamp()
        #time = float(s.recv(1024).decode())
        #resTime = datetime.now().timestamp()
        #delay = resTime - reqTime
        #cristian = delay / 2
        #time += cristian
        state = True
        while True:
            data = s.recv(1024).decode()
            print(data)
            if not data:
                raise Exception
            elif data[0] == '{':
                data = json.loads(data)
                book = data['bookTitle']
            elif data[0] == '&':
                print('Llego aqui')
                raise Exception('Disconnect')
            else:
                time = float(data)
    except Exception as ex:
        print(ex)
        Book = 'Disconnected'
        time = 0
        state = False

if __name__ == '__main__':
    sg.theme('DarkBlue16')
    layout = [
        [sg.Text('No book', size=(100, 0),key='book', justification='center')],
        [sg.Text('Disconnected', size=(100, 0),key='status', justification='center')],
        [sg.Text('Direccion ip:'), sg.InputText(key='ip_port')],
        [sg.Button('Connect'), sg.Button('Ask for book')],
    ]
    window = sg.Window('Client', layout, size=(410,130), font='Helvetica 12')
    while True:
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            s.close()
            break
        elif event == 'Connect':
            ip = values['ip_port'][:values['ip_port'].find(':')]
            port = int(values['ip_port'][values['ip_port'].find(':') + 1:])
            addr = (ip, port)
            t = threading.Thread(target=clientSocket, args=(addr, ), name='conn')
            t.daemon = True
            t.start()
        elif event == 'Ask for book':
            s.send('0'.encode())
        if time != 0:
            strdate = str(datetime.fromtimestamp(time))[11:-4]
            window.Element('status').Update('Connected - {}'.format(strdate))
            time += 0.01
        if time == 0:
            book = ''
            window.Element('status').Update('Disconnected')
        if book != '':
            window.Element('book').Update('Book booked: {}'.format(book))
        if state:
            window.Element('Connect').Update(disabled=True)
            window.Element('Ask for book').Update(disabled=False)
        if not state:
            window.Element('Connect').Update(disabled=False)
        if not state or book != '':
            window.Element('Ask for book').Update(disabled=True)