###SMTP-CLIENT###
#!/usr/bin/env python3

import socket
import os
import sys

#pull data from the client.conf file
config = open("client.conf", 'r')
configValues = config.read()
configList = configValues.split('\n')
SERVER_IP = configList[0]
SERVER_PORT = configList[1]
delim = '='
SERVER_IP = SERVER_IP.split(delim, 1)[1]
SERVER_PORT = SERVER_PORT.split(delim, 1)[1]
print('server IP: ', SERVER_IP, '\n', 'server port: ', SERVER_PORT, '\n\n')
config.close()

def printResponse(response):
    print('from server -> ', response, '\n')
    return

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliSock:
    cliSock.connect((SERVER_IP, int(SERVER_PORT)))
    print('connected to ', SERVER_IP, ' on port ', SERVER_PORT, '\n\n')
    while True:
        msg = input("message for the server(HELP: if you need help): ")
        if msg == 'QUIT':
            cliSock.sendall('QUIT'.encode())
            data = cliSock.recv(1024)
            print('from server->', str(data.decode()))
            break
        elif msg == 'DATA':
            cliSock.sendall(msg.encode())
            data = str(cliSock.recv(1024).decode())
            printResponse(data)
            print('enter message, end with . on empty line\n')
            msg = ''
            while True:
                dummy = input() + '\n'
                if dummy == '.\n':
                    break
                msg += dummy

        cliSock.sendall(msg.encode())
        data = str(cliSock.recv(1024).decode())
        if data[0] == '5':
            print('server sent 500 error reply, closing down..')
            sys.exit()
        printResponse(data)

#return to driver options menu
os.system('python client-driver.py')


