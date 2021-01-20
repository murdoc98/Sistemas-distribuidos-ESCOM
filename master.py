import PySimpleGUI as sg
import threading
import time
from socket import socket 
from datetime import datetime
from dateutil import parser
clk = {
    'clk1': 0,
    'clk2': 0,
    'clk3': 0
}
addr = {
    'addr1': '###.###.###.###:######',
    'addr2': '###.###.###.###:######',
    'addr3': '###.###.###.###:######'
}
strclk = {
    'strclk1': '',
    'strclk2': '',
    'strclk3': ''
}
flag = {
    'flag1': False,
    'flag2': False,
    'flag3': False
}
threads = ['1', '2', '3']
def multi_threaded_client(connection, address):
    global clk
    global addr
    global flag
    global threads
    threadName = threading.currentThread().getName()
    address = str(address)
    connection.send(strtimestamp.encode())
    data = connection.recv(1024).decode()
    if data:
        clk['clk' + threadName] = parser.parse(data).timestamp()
        addr['addr' + threadName] = address[2:address.find(',')-1] + ':' + address[address.find(',')+1:-1]
    while True:
        time.sleep(1)
        if flag['flag' + threadName]:
            connection.send(strclk['strclk'+threadName].encode())
            flag['flag' + threadName] = False
    connection.close()

def serverSocket():
    global threads
    threadName = threading.currentThread().getName()
    print('Escuchando desde el hilo: {}'.format(threadName))
    s = socket()
    s.bind(('', 8001))
    s.listen(3)
    while True:
        client, address = s.accept()
        t = threading.Thread(target=multi_threaded_client, args=(client, address, ), name=threads.pop())
        t.start()

sg.theme('DarkAmber')
layout = [
    [sg.Text(size=(100, 1),key='masterClock', justification='center')],
    [
        sg.Text('Clock 1'), 
        sg.Text('###.###.###.###:######', key='addr1'), 
        sg.Text('####-##-## ##:##:##.##', key='clk1', justification='center')
    ],[
        sg.Text('Nueva hora: '), 
        sg.InputText(key='newClk1'),
        sg.Button('Sync', key='syncClk1')
    ],[
        sg.Text('Clock 2'), 
        sg.Text('###.###.###.###:######', key='addr2'), 
        sg.Text('####-##-## ##:##:##.##', key='clk2', justification='center'),
    ],[
        sg.Text('Nueva hora: '), 
        sg.InputText(key='newClk2'),
        sg.Button('Sync', key='syncClk2')
    ],[
        sg.Text('Clock 3'), 
        sg.Text('###.###.###.###:######', key='addr3'), 
        sg.Text('####-##-## ##:##:##.##', key='clk3', justification='center'),
    ],[
        sg.Text('Nueva hora: '), 
        sg.InputText(key='newClk3'),
        sg.Button('Sync', key='syncClk3')
    ]
]

# Create the window
window = sg.Window('Master clock', layout, size=(850,320), font="Helvetica 18")
# Get local time
now = datetime.now()
timestamp = datetime.timestamp(now)
strclk1 = ''
strclk2 = ''
strclk3 = ''
serverSocket = threading.Thread(target=serverSocket, name='server')
serverSocket.start()
# Create an event loop
while True:
    event, values = window.read(timeout=10)
    timestamp += 0.01
    strtimestamp = str(datetime.fromtimestamp(timestamp))
    # End program if user closes window or
    # presses the OK button
    if clk['clk1'] != 0:
        clk['clk1'] += 0.01
        strclk['strclk1'] = str(datetime.fromtimestamp(clk['clk1']))
    if clk['clk2'] != 0:
        clk['clk2'] += 0.01
        strclk['strclk2'] = str(datetime.fromtimestamp(clk['clk2']))
    if clk['clk3'] != 0:
        clk['clk3'] += 0.01
        strclk['strclk3'] = str(datetime.fromtimestamp(clk['clk3']))
    if clk['clk1'] == 0:
        strclk['strclk1'] = '####-##-## ##:##:##.##'
    if clk['clk2'] == 0:
        strclk['strclk2'] = '####-##-## ##:##:##.##'
    if clk['clk3'] == 0:
        strclk['strclk3'] = '####-##-## ##:##:##.##'
    # Events
    if event == sg.WIN_CLOSED:
        break
    if event == "syncClk1":
        clk['clk1'] = parser.parse(values['newClk1']).timestamp()
        flag['flag1'] = True
    if event == "syncClk2":
        clk['clk2'] = parser.parse(values['newClk2']).timestamp()
        flag['flag2'] = True
    if event == "syncClk3":
        clk['clk3'] = parser.parse(values['newClk3']).timestamp()
        flag['flag3'] = True
    window.Element('masterClock').Update(strtimestamp[:-4])
    window.Element('clk1').Update(strclk['strclk1'][:-4])
    window.Element('clk2').Update(strclk['strclk2'][:-4])
    window.Element('clk3').Update(strclk['strclk3'][:-4])
    window.Element('addr1').Update(addr['addr1'])
    window.Element('addr2').Update(addr['addr2'])
    window.Element('addr3').Update(addr['addr3'])
