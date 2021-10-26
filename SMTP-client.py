###SMTP-CLIENT###
#!/usr/bin/env python3

import socket
import os
import sys
import base64

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
print(('<><><><><><><><><><><><><><><><><><><><><><><>\n'
       '<><><> Enter \'HELP\' if you need help <><><><>\n'
       '<><><><><><><><><><><><><><><><><><><><><><><>\n'))

def printResponse(response):
    if type(response) is str:
        print('from server:\n', response, '\n')
    else:
        print('from server:\n', response.decode(), '\n')

def returnToMenu():
    os.system('python client-driver.py')

# this is used for all user input
def promptUser(cliSock, display, command):
    while True:
        msg = input(display)
        if msg[0:4] == 'HELP':
            cliSock.sendall('HELP'.encode())
            data = cliSock.recv(1024)
            printResponse(data.decode())
        elif msg[0:4] == 'QUIT':
            cliSock.sendall('QUIT'.encode())
            data = cliSock.recv(1024)
            printResponse(data.decode())
            cliSock.close()
            sys.exit()
        elif msg == '':
            cliSock.sendall('HELP'.encode())
            data = cliSock.recv(1024)
            printResponse(data)
        elif display == 'username: ':
            msg = msg.encode()
            msg = base64.b64encode(msg)
            cliSock.sendall(msg)
            data = cliSock.recv(1024)
            respCode = data.decode()[0:3]
            if respCode == '330':
                data = data.decode()[4:]
                data = data.encode()
                data = base64.b64decode(data)  # add padding?
                data = data.decode()
                printResponse('330 ' + data)
                print('new credentials received, closing down..')
                sys.exit()
            elif respCode == '334':
                printResponse(data.decode())
                return

            printResponse(data)

        elif display == 'password: ':
            msg = msg.encode()
            msg = base64.b64encode(msg)
            cliSock.sendall(msg)
            # will either be 235 good, or something else
            data = cliSock.recv(1024).decode()
            #this is 235 good auth
            if data[0:3] == '235':
                printResponse(data)
                return

            printResponse(data)

        else: # for every other command
            cliSock.sendall((command + msg).encode())
            data = cliSock.recv(1024)
            #if error is given, loop back around
            if data[0] == '5' or data[0] == '4':
                printResponse(data)
                continue
            printResponse(data)
            return

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliSock:
    cliSock.connect((SERVER_IP, int(SERVER_PORT)))
    print('connected to ', SERVER_IP, ' on port ', SERVER_PORT, '\n\n')
    # this will send commands in correct order
    while True:

        promptUser(cliSock, 'domain name: ', 'HELO:')

        cliSock.sendall('AUTH'.encode())
        data = cliSock.recv(1024)
        printResponse(data)
        promptUser(cliSock, 'username: ', '')
        promptUser(cliSock, 'password: ', '')

        promptUser(cliSock, 'Mail From: ', 'MAIL FROM:')
        promptUser(cliSock, 'To: ', 'RCPT TO:')

        cliSock.sendall('DATA'.encode())
        data = cliSock.recv(1024)
        printResponse(data)
        print('Message (end with . on blank line):\n')
        msg = ''
        while True:
            dummy = input() + '\n'
            if dummy == '.\n':
                break
            msg += dummy

        cliSock.sendall(msg.encode())
        data = cliSock.recv(1024)
        printResponse(data)

        returnToMenu()

# #return to driver options menu
# os.system('python client-driver.py')


