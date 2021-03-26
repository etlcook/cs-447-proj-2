###SMTP-SERVER###
#!/usr/bin/env python3

import socket
import os
import sys
import threading
import datetime

def createDBifNeeded():
    #create db folder if not exists
    path = os.getcwd()
    path = path + '/db'
    if not os.path.exists(path):
        os.mkdir(path)

def readFromConf():
    #pull data from the server.conf file
    config = open('server.conf', 'r')
    configValues = config.read()
    configList = configValues.split('\n')
    otherServers = []
    i = 0
    for line in configList:
        if line == '[SELF]':
            DOMAIN = str(configList[i + 1]).split("=")[1]
            SMTP_PORT = str(configList[i + 2]).split("=")[1]
            HTTP_PORT = str(configList[i + 3]).split("=")[1]

        #add all other server info to list, stored as [ip1, port1, ip2, port2, ...]
        elif line == '[REMOTE]':
            otherDomain = str(configList[i + 1]).split("=")[1]
            otherIP = str(configList[i + 2]).split("=")[1]
            otherPort = str(configList[i + 3]).split("=")[1]
            otherServers.append(otherDomain)
            otherServers.append(otherIP)
            otherServers.append(otherPort)

        i = i + 1

    print('SMTP port: ', SMTP_PORT, '\n')

    config.close()
    return DOMAIN, SMTP_PORT, HTTP_PORT, otherServers

def helo(conn):
    while True:
        data = conn.recv(1024).decode()
        if data[:4] == 'HELO':
            conn.sendall("250 OK HELO".encode())
            return data
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            sys.exit()

def mailfrom(conn): #TODO: make sure user is the same domain as the server, unless coming from a known server
    while True:
        data = conn.recv(1024).decode()
        if data[:9] == 'MAIL FROM':
            conn.sendall("250 OK MAIL FROM".encode())
            return data[10:]
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            sys.exit()

def rcptto(conn):
    while True:
        data = conn.recv(1024).decode()
        if data[:7] == 'RCPT TO':
            conn.sendall("250 OK RCPT TO".encode())
            return data
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            sys.exit()

def data(conn):
    while True:
        data = conn.recv(1024).decode()
        if data[:4] == 'DATA':
            conn.sendall("354 Intermediate".encode())
            data2 = conn.recv(1024).decode()
            conn.sendall("250 OK DATA".encode())
            return data2
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            sys.exit()

def quitAll(conn):
    conn.sendall('221 Goodbye'.encode())
    sys.exit()

def help(conn):
    conn.sendall(("\t1. HELO:<IP ADDRESS>\n\t2. MAIL FROM:<YOUR EMAIL ADDRESS>\n\t"
                 "3. RCPT TO:<RECIPIENT EMAIL ADDRESS>\n\t4. DATA:<MESSAGE FOR THE RECIPIENT>\n\t"
                 "5. QUIT to end session\n\nType your command first, followed by a colon, and then "
                 "your information.\nWhen writing your DATA, enter DATA and hit enter first, "
                 "then write your message.\nEnd with . on newline.\n\n").encode())

def handleEmailSending(senderAddress, receivingUsers, emailString, DOMAIN, otherServers):
    def localDomain():
        path = os.getcwd()
        userPath = 'db/' + username
        fullUserPath = os.path.join(path, userPath)
        # make db entry for user if not exists
        if not os.path.exists(fullUserPath):
            os.makedirs(fullUserPath)
            k = open(fullUserPath + '/nextnum.txt', 'w')
            k.write(str(int(1)))
            k.close()
        # read next number for email file name and increment
        z = open(fullUserPath + '/nextnum.txt', 'r')
        fnum = int(z.read())
        z.close()
        nextFileNum = int(fnum) + 1
        # increment file for next time
        s = open(fullUserPath + '/nextnum.txt', 'w')
        s.write(str(nextFileNum))
        s.close()

        # create new email file in user db folder
        newEmailFile = str(fnum) + '.email'
        newEmailFile = userPath + '/' + newEmailFile
        j = open(newEmailFile, 'w')
        j.write(emailString)
        j.close()

    #this is where the server communicates with the other server
    def remoteDomain():
        i = 0
        #iterate through list of remote servers given in conf file until we see the domain we need; grab IP and port
        for elem in otherServers:
            if otherServers[i] == userDomain:
                remoteIP = otherServers[i + 1]
                remotePort = otherServers[i + 2]
            i = i + 1

        #TODO: connect to smtp server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as senderSock:
            senderSock.connect((remoteIP, int(remotePort)))
            print('connected to ', remoteIP, ' on port ', remotePort, '\n\n')
            senderSock.sendall(("HELO:" + DOMAIN).encode())
            response = senderSock.recv(1024).decode()
            senderSock.sendall(("MAIL FROM:" + senderAddress).encode())
            response = senderSock.recv(1024).decode()
            senderSock.sendall(("RCPT TO:" + emailAddress).encode())
            response = senderSock.recv(1024).decode()
            senderSock.sendall(("DATA").encode())
            response = senderSock.recv(1024).decode()
            senderSock.sendall((emailString).encode())
            response = senderSock.recv(1024).decode()

    for emailAddress in receivingUsers:
        # make user paths that don't exist
        # make sure this is valid domain
        if '@' not in emailAddress:
            conn.sendall('500 error: \'' + emailAddress + '\' is not a valid address')
            sys.exit()
        # separate username from domain
        userSplit = emailAddress.split('@')  # can use userSplit[1] to see domain!
        username = userSplit[0]
        userDomain = userSplit[1]

        #handle email appropriatly based on the receiver being the servers domain or a different server
        if userDomain == DOMAIN:
            localDomain()
        elif userDomain in otherServers:
            remoteDomain()
        else:
            print('the domain: ' + str(userDomain) + ' is not recognised. skipping..')
            continue



    conn.sendall(emailString.encode())

#userType is either 'client' or 'server' depending on who is connected through SMTP port
def main(servSock, conn, addr, DOMAIN, userType, otherServers):
    #TODO: implement difference in client-server versus server-server
    with conn:
        while True:

            heloData = helo(conn)
            senderAddress = mailfrom(conn)
            rcpttoData = rcptto(conn)
            dataData = data(conn)

            userEmail = 'Date: ' + str(datetime.datetime.now()) + '\nFrom: ' + senderAddress + '\nTo: ' + str(rcpttoData[8:]) + '\nMessage:\n' + str(dataData) + '\n'
            print(userEmail)

            #get email addresses from RCPT TO data
            recUsers = rcpttoData.split(':')
            recUsers = recUsers[1]
            recUsers = recUsers.split()

            #encapsulate everything below into this and subsequent functions
            print('\nthis is where the fun begins..\n')
            handleEmailSending(senderAddress, recUsers, userEmail, DOMAIN, otherServers)
            #TODO: delete rest after above funct complete

            # for user in recUsers:
            #     #make user paths that don't exist
            #     #make sure this is valid domain
            #     if '@' not in user:
            #         conn.sendall('500 error: \'' + user + '\' is not a valid address')
            #         sys.exit()
            #     #separate username from domain
            #     userSplit = user.split('@') #can use userSplit[1] to see domain!
            #     username = userSplit[0]
            #     userDomain = userSplit[1]
            #
            #     path = os.getcwd()
            #     userPath = 'db/' + username
            #     fullUserPath = os.path.join(path, userPath)
            #     #make db entry for user if not exists
            #     if not os.path.exists(fullUserPath):
            #         os.makedirs(fullUserPath)
            #         k = open(fullUserPath + '/nextnum.txt', 'w')
            #         k.write(str(int(1)))
            #         k.close()
            #     #read next number for email file name and increment
            #     z = open(fullUserPath + '/nextnum.txt', 'r')
            #     fnum = int(z.read())
            #     z.close()
            #     nextFileNum = int(fnum) + 1
            #     #increment file for next time
            #     s = open(fullUserPath + '/nextnum.txt', 'w')
            #     s.write(str(nextFileNum))
            #     s.close()
            #
            # #create new email file in user db folder
            # newEmailFile = str(fnum) + '.email'
            # newEmailFile = userPath + '/' + newEmailFile
            # j = open(newEmailFile, 'w')
            # j.write(userEmail)
            # j.close()
            #
            # conn.sendall(userEmail.encode())

if __name__ == "__main__":
    createDBifNeeded()
    DOMAIN, SMTP_PORT, HTTP_PORT, otherServers = readFromConf()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servSock:
        servSock.bind(('', int(SMTP_PORT)))
        servSock.listen(5)
        print("server is running...")
        while True:
            conn, addr = servSock.accept()
            if addr in otherServers:
                print('\nConnected by server: ', addr)
                try:
                    x = threading.Thread(target=main, args=(servSock, conn, addr, DOMAIN, 'server', otherServers))
                    x.start()
                except threading.error as e:
                    print(str(e))
                    print('closing from threading exception..')
                    sys.exit()
            else:
                print('\nConnected by client: ', addr)
                try:
                    x = threading.Thread(target=main, args=(servSock, conn, addr, DOMAIN, 'client', otherServers))
                    x.start()
                except threading.error as e:
                    print(str(e))
                    print('closing from threading exception..')
                    sys.exit()
