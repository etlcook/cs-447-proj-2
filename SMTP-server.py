###SERVER###
#!/usr/bin/env python3

import socket
import os

# this creates db folder for recipient directories
path = os.getcwd()
path = path + '/db'
if not os.path.exists(path):
    os.mkdir(path)

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)

#the following lines connect to the config file, reading in the values needed
config = open('server.conf', 'r')
configValues = config.read()
configList =  configValues.split('\n')
SMTP_PORT = configList[0]
delim = '='
SMTP_PORT = SMTP_PORT.split(delim, 1)[1]
print('SMTP port: ', SMTP_PORT, '\n')
config.close()

def helo(command):
    if command[0:4] == 'HELO':
        conn.sendall(bytes("250 HELO OK", 'utf-8'))
        return
    else:
        conn.sendall(bytes("500, introduce yourself with HELO first", 'utf-8'))
        conn.close()
        quit()

def mailfrom(command):
    if command[0:9] == 'MAIL FROM':
        conn.sendall(bytes("250 OK MAIL FROM", 'utf-8'))
        return
    else:
        conn.sendall(bytes("500, expected MAIL FROM", 'utf-8'))
        conn.close()
        quit()

def rcptto(command):
    if command[0:7] == 'RCPT TO':
        conn.sendall(bytes("250 OK RCPT TO", 'utf-8'))
        return
    else:
        conn.sendall(bytes("500, expected RCPT TO", 'utf-8'))
        conn.close()
        quit()

def data(command):
    if command[0:4] == 'DATA':
        conn.sendall(bytes("250 OK DATA", 'utf-8'))
        return
    else:
        conn.sendall(bytes("500, expected DATA", 'utf-8'))
        conn.close()
        quit()

def quitAll():
    conn.sendall(bytes('221 Goodbye', 'utf-8'))
    conn.close()
    quit()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servSock:
    servSock.bind(('', int(SMTP_PORT)))
    servSock.listen()
    print("server is running...")
    global conn, addr
    conn, addr = servSock.accept()
    with conn:
        print('Connected by', addr)
        while True:
            heloData = conn.recv(1024).decode()
            if heloData == 'QUIT':
                quitAll()
            helo(heloData)

            mailfromData = conn.recv(1024).decode()
            if mailfromData == 'QUIT':
                quitAll()
            mailfrom(mailfromData)

            rcpttoData = conn.recv(1024).decode()
            if rcpttoData == 'QUIT':
                quitAll()
            rcptto(rcpttoData)

            dataData = conn.recv(1024).decode()
            if dataData == 'QUIT':
                quitAll()
            data(dataData)

            userEmail = 'FROM: ' + str(mailfromData[10:]) + '\nTO: ' + str(rcpttoData[8:]) + '\nMESSAGE: ' + str(dataData[5:]) + '\n\n'
            print(userEmail)
            
            #get username from RCPT TO data
            recUsers = rcpttoData.split()
            recUsers = recUsers[2:]
            for user in recUsers:
                #make user paths that don't exist
                username = user[:-8]
                path = os.getcwd()
                userPath = 'db/' + username
                fullUserPath = os.path.join(path, userPath)
                if not os.path.exists(fullUserPath):
                    
                    os.makedirs(fullUserPath)
                    k = open(fullUserPath + '/nextnum.txt', 'w')
                    k.write(str(int(1)))
                    k.close()
                #read next number for email file name and increment
                z = open(fullUserPath + '/nextnum.txt', 'r')
                fnum = int(z.read()) 
                z.close()
                nextFileNum = int(fnum) + 1
                #increment file for next time
                s = open(fullUserPath + '/nextnum.txt', 'w')
                s.write(str(nextFileNum))
                s.close()

            #create new user folder and email file in user folder
            newEmailFile = str(fnum) + '.email'
            newEmailFile = userPath + '/' + newEmailFile
            j = open(newEmailFile, 'w')
            j.write(userEmail)
            j.close()

            conn.sendall(bytes(userEmail, 'utf-8'))

#loop back to server options menu
os.system('server-driver.py')

