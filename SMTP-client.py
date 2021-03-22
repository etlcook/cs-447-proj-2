###CLIENT###
#!/usr/bin/env python3

import socket
DOMAIN = '447.edu'

#the following lines connect to the config file, reading in the values needed
configName = input("enter name of config file: ")
config = open(configName, 'r')
configValues = config.read()
configList =  configValues.split('\n')
SERVER_IP = configList[0]
SERVER_PORT = configList[1]
#SERVER_IP = '192.168.0.10'  #REMOVE
#SERVER_PORT = '25' #REMOVE
delim = '='
SERVER_IP = SERVER_IP.split(delim, 1)[1]
SERVER_PORT = SERVER_PORT.split(delim, 1)[1]
print('server IP: ', SERVER_IP, '\n', 'server port: ', SERVER_PORT, '\n\n')
config.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliSock:
    cliSock.connect((SERVER_IP, int(SERVER_PORT)))
    print('connected to ', SERVER_IP, ' on port ', SERVER_PORT, '\n\n')
    while True:
        msg = input("message for the server(HELP if you need help): ")
        if msg == 'QUIT':
            cliSock.sendall(bytes('QUIT', 'utf-8'))
            data = cliSock.recv(1024)
            print('from server->', repr(data))
            break
        elif msg == 'DATA':
            print('enter message, end with . on empty line\n')
            msg = ''
            while True:
                dummy = input() + '\n'
                if dummy == '.\n':
                    break
                msg += dummy
            msg = 'DATA ' + msg
        elif msg == 'HELP':
            print("\t1. HELO <IP ADDRESS>\n\t2. MAIL FROM <YOUR EMAIL ADDRESS>\n\t3. RCPT TO <RECIPIENT EMAIL ADDRESS>\n\t4. DATA <MESSAGE FOR THE RECIPIENT>\n\t5. QUIT to end session\n\nType your command first, followed by a space, and then your information.\nWhen writing your DATA, enter DATA and hit enter first, then write your message.\nEnd with . on newline.\n\n")
            continue

        cliSock.sendall(bytes(msg, 'utf-8'))
        data = cliSock.recv(1024)
        print('from server-> ', repr(data))

    
