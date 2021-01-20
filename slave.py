import PySimpleGUI as sg
from socket import socket 
from timeit import default_timer as timer
from datetime import datetime, timedelta
from dateutil import parser
import threading
def multi_threaded_client(ip, port):
    global timestamp
    s.connect((ip, int(port)))
    request_time = timer()
    server_time = parser.parse(s.recv(1024).decode())
    response_time = timer()
    process_delay_latency = response_time - request_time
    cristian = timedelta(seconds = (process_delay_latency) / 2)
    client_time = server_time + cristian
    timestamp = client_time.timestamp()
    s.send(str(client_time + cristian).encode())
    while True:
        data = s.recv(1024).decode()
        if data:
            print(timestamp)
            timestamp = parser.parse(data).timestamp()
            print(timestamp)
        if not data:
            break
    connection.close()

sg.theme('DarkAmber')  
layout = [
    [sg.Text('####-##-## ##:##:##.##', size=(100, 1),key='clock', justification='center')],
    [sg.Text('Direccion ip:'), sg.InputText(key='ip_port')],
    [sg.Button('Connect'), sg.Button('Disconnect')],
]

# Create the window
window = sg.Window('Slave clock', layout, size=(400,150), font="Helvetica 18")
s = socket()
timestamp = 0
while True:
    event, values = window.read(timeout=10)
    if(timestamp > 0):
        timestamp += 0.01
        strtimestamp = str(datetime.fromtimestamp(timestamp))
        window.Element('Connect').Update(disabled=True)
        window.Element('Disconnect').Update(disabled=False)
    if(timestamp == 0):
        strtimestamp = '####-##-## ##:##:##.##'
        window.Element('Connect').Update(disabled=False)
        window.Element('Disconnect').Update(disabled=True)
    if event == 'Connect':
        ip = values['ip_port'][:values['ip_port'].find(':')]
        port = values['ip_port'][values['ip_port'].find(':') + 1:]
        t = threading.Thread(target=multi_threaded_client, args=(ip, port, ), name='thread2')
        t.start()
        timestamp = 0
    if event == 'Disconnect':
        s.close()
        s = socket()
        timestamp=0
    if event == sg.WIN_CLOSED:
        s.close()
        break
    window.Element('clock').Update(strtimestamp[:-4])