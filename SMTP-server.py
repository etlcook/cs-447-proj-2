###SMTP-SERVER###
# !/usr/bin/env python3

import socket
import os
import sys
import string
import random
import base64
import threading
import datetime

def createDBifNeeded():
    # create db folder if not exists
    path = os.getcwd()
    path = path + '/db'
    if not os.path.exists(path):
        os.mkdir(path)
    # create hidden username:password file if not exists
    if not os.path.exists(path + "/.user_pass"):
        k = open(path + '/.user_pass', 'w')
        k.close()
    # create hidden server log file if not exists
    if not os.path.exists(path + "/.server_log"):
        print('creating hidden server_log file')
        q = open(path + '/.server_log', 'w')
        q.close()

def readFromConf():
    # pull data from the server.conf file
    config = open('server.conf', 'r')
    configValues = config.read()
    configList = configValues.split('\n')
    otherServers = []
    i = 0
    for line in configList:
        if line == '[SELF]':
            DOMAIN = str(configList[i + 1]).split("=")[1]
            SELF_IP = str(configList[i + 2]).split("=")[1]
            SMTP_PORT = str(configList[i + 3]).split("=")[1]
            HTTP_PORT = str(configList[i + 4]).split("=")[1]

        # add all other server info to list, stored as [ip1, port1, ip2, port2, ...]
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
    return DOMAIN, SELF_IP, SMTP_PORT, HTTP_PORT, otherServers

def helo(conn):
    while True:
        data = conn.recv(1024).decode()
        logActs('HELO', 'na', '', 'in')
        if data[:4] == 'HELO':
            conn.sendall("250 OK HELO".encode())
            logActs('HELO', '250', 'OK')
            return data
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            logActs('HELO', '503', 'bad sequence of commands')
            sys.exit()

def auth(conn):
    while True:
        data = conn.recv(1024).decode()
        logActs('AUTH', 'na', 'AUTH command', 'in')
        if data == 'AUTH':
            conn.sendall("334 dXNlcm5hbWU6".encode())
            logActs('AUTH', '334 dXNlcm5hbWU6', '')
            username = base64.b64decode(conn.recv(1024))
            logActs('AUTH', 'na', 'username captured', 'in')
            username = username.decode()
            # here we see if user is new or existing
            path = os.getcwd() + "/db/.user_pass"
            credFile = open(path, 'r')
            credString = str(credFile.read())
            exists = False
            credList = credString.split('\n')
            for item in credList:
                keyValPair = item.split(':')
                if keyValPair[0] == username:
                    truePassword = keyValPair[1]
                    exists = True
                    break
            credFile.close()
            # if new user, make them a password and end connection
            if exists is False:
                authNew(conn, username)
                quitAll(conn)

            conn.sendall("334 cGFzc3dvcmQ6".encode())
            logActs('AUTH', '334 cGFzc3dvcmQ6', '')
            while True:
                password = base64.b64decode(conn.recv(1024))
                logActs('AUTH', 'na', 'password captured', 'in')
                password = password.decode()
                password = '447S21' + password
                password = password.encode()
                password = base64.b64encode(password)
                if str(password) == truePassword:
                    conn.sendall("235 AUTH successful".encode())
                    logActs('AUTH', '235', 'successfull AUTH')
                    return username
                else:
                    conn.sendall("535 invalid credentials. re-enter password".encode())
                    logActs('AUTH', '535', 'invalid credentials')

        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            logActs('AUTH', '503', 'bad sequence of commands')
            sys.exit()

def mailfrom(conn):
    while True:
        data = conn.recv(1024).decode()
        logActs('MAIL FROM', 'na', '', 'in')
        if data[:9] == 'MAIL FROM':
            conn.sendall("250 OK MAIL FROM".encode())
            logActs('MAIL FROM', '250', 'OK')
            return data[10:]
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            logActs('MAIL FROM', '503', 'bad sequence of commands')
            sys.exit()

def rcptto(conn):
    while True:
        data = conn.recv(1024).decode()
        logActs('RCPT TO', 'na', '', 'in')
        if data[:7] == 'RCPT TO':
            conn.sendall("250 OK RCPT TO".encode())
            logActs('RCPT TO', '250', 'OK')
            return data
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            logActs('RCPT TO', '503', 'bad sequence of commands')
            sys.exit()

def data(conn):
    while True:
        data = conn.recv(1024).decode()
        logActs('DATA', 'na', 'DATA command', 'in')
        if data[:4] == 'DATA':
            conn.sendall("354 Intermediate".encode())
            logActs('DATA', '354', 'Intermediate')
            data2 = conn.recv(1024).decode()
            logActs('DATA', 'na', 'DATA email body', 'in')
            conn.sendall("250 OK DATA".encode())
            logActs('DATA', '250', 'OK')
            return data2
        elif data == 'QUIT':
            quitAll(conn)
        elif data[:4] == 'HELP':
            help(conn)
        else:
            conn.sendall("503 bad sequence of commands".encode())
            logActs('DATA', '503', 'bad sequence of commands')
            sys.exit()

def quitAll(conn):
    conn.sendall('221 Goodbye'.encode())
    logActs('QUIT', '221', 'Goodbye')
    sys.exit()

def help(conn):
    conn.sendall((
                     "\n\t1. HELO:<IP ADDRESS>\n\t2. AUTH<hit enter>\n\t4. <username>\n\t5. <password>\n\t6. MAIL FROM:<YOUR EMAIL ADDRESS>\n\t"
                     "7. RCPT TO:<RECIPIENT EMAIL ADDRESS>\n\t8. DATA:<MESSAGE FOR THE RECIPIENT>\n\t"
                     "9. QUIT to end session\n\nType your command first, followed by a colon, and then "
                     "your information.\nWhen writing your DATA, type \'DATA\' and hit enter first, "
                     "then write your message.\nEnd DATA message with . on newline.\n").encode())
    logActs('HELP', '250', 'help string provided')

# this will create a new user entry, and send autogenerated password back to user
def authNew(conn, username):
    source = string.ascii_letters + string.digits
    password = ''.join((random.choice(source) for i in range(6)))
    prefixPass = '447S21' + str(password)
    prefixPass = prefixPass.encode()
    saltedPassword = base64.b64encode(prefixPass)
    path = os.getcwd() + "/db/.user_pass"
    credFile = open(path, 'a+')
    credStr = credFile.read()
    credStr = credStr + username + ':' + str(saltedPassword) + '\n'
    credFile.write(credStr)
    credFile.close()
    msg = password
    msg = msg.encode()
    msg = base64.b64encode(msg)
    conn.sendall(b'330 ' + msg)
    logActs('AUTH', '330', 'autogenerated password')
    return

# makes sure email arguments are cohesive
def validateUser(username, senderAddress, DOMAIN): # todo:email sender error report
    moniker, dom = senderAddress.split('@')
    if moniker == username and dom == DOMAIN:
        return True
    else:
        print('unauthorized sending of email, ' + senderAddress + ' doesnt match username '
                                                                  'or domain isn\'t valid for this server. closing..')
        return False

# this will handle emails differently whether sent to a remote or local user
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

    # this is where the server communicates with the other server
    def remoteDomain():
        i = 0
        # iterate through list of remote servers given in conf file until we see the domain we need; grab IP and port
        for elem in otherServers:
            if otherServers[i] == userDomain:
                remoteIP = otherServers[i + 1]
                remotePort = otherServers[i + 2]
            i = i + 1

        emailBody = emailString.split("Message:\n")[1]

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as senderSock:
            senderSock.connect((remoteIP, int(remotePort)))
            print('connected to ', remoteIP, ' on port ', remotePort, '\n\n')
            senderSock.sendall(("HELO:" + DOMAIN).encode())
            logActs('HELO', 'na', 'remote sending', 'out', remoteIP)
            response = senderSock.recv(1024).decode()
            logActs('HELO', 'na', 'remote response', 'in', remoteIP)
            senderSock.sendall(("MAIL FROM:" + senderAddress).encode())
            logActs('MAIL FROM', 'na', 'remote sending', 'out', remoteIP)
            response = senderSock.recv(1024).decode()
            logActs('MAIL FROM', 'na', 'remote response', 'in', remoteIP)
            senderSock.sendall(("RCPT TO:" + emailAddress).encode())
            logActs('RCPT TO', 'na', 'remote sending', 'out', remoteIP)
            response = senderSock.recv(1024).decode()
            logActs('RCPT TO', 'na', 'remote response', 'in', remoteIP)
            senderSock.sendall(("DATA").encode())
            logActs('DATA', 'na', 'remote sending DATA command', 'out', remoteIP)
            response = senderSock.recv(1024).decode()
            logActs('DATA', 'na', 'remote response', 'in', remoteIP)
            senderSock.sendall((emailBody).encode())
            logActs('DATA', 'na', 'remote sending DATA email body', 'out', remoteIP)
            response = senderSock.recv(1024).decode()
            logActs('DATA', 'na', 'remote response DATA email body', 'in', remoteIP)

    for emailAddress in receivingUsers:
        # make user paths that don't exist
        # make sure this is valid domain
        if '@' not in emailAddress: # todo:email sender error report
            conn.sendall('500 error: \'' + emailAddress + '\' is not a valid address')
            logActs('post-processing', '500', 'invalid email address')
            sys.exit()
        # separate username from domain
        userSplit = emailAddress.split('@')  # can use userSplit[1] to see domain!
        username = userSplit[0]
        userDomain = userSplit[1]

        # handle email appropriatly based on the receiver being the servers domain or a different server
        if userDomain == DOMAIN:
            localDomain()
        elif userDomain in otherServers:
            remoteDomain()
        else:
            print('the domain: ' + str(userDomain) + ' is not recognised. skipping..')
            continue

# this logs to the standard output and to the server_log file
def logActs(command, code, description = '', msgDirection = 'out', remIP = ''):
    logPath = os.getcwd() + '/db/.server_log'
    logFile = open(logPath, 'a')
    if not remIP:
        remIP = addr[0]
    if msgDirection == 'out':
        logString = str(datetime.datetime.now())
        logString += ' from-' + SELF_IP + ' to-' + remIP + ' SMTP-' + command + ' ' + code + ' ' + description
        logFile.write(logString)
        print(logString)
        logFile.close()
    elif msgDirection == 'in':
        logString = str(datetime.datetime.now())
        logString += ' from-' + remIP + ' to-' + SELF_IP + ' SMTP-' + command + ' ' + code + ' ' + description
        logFile.write(logString)
        print(logString)
        logFile.close()

# userType is either 'client' or 'server' depending on who is connected through SMTP port
def main(servSock, conn, addr, DOMAIN, userType, otherServers):
    if userType == 'client':
        while True:

            heloData = helo(conn)
            username = auth(conn)
            senderAddress = mailfrom(conn)
            rcpttoData = rcptto(conn)
            dataData = data(conn)

            # make sure moniker == username and server domain matches sender email domain
            if not validateUser(username, senderAddress, DOMAIN):
                # log
                conn.close()
                sys.exit()

            userEmail = 'Date: ' + str(datetime.datetime.now()) + '\nFrom: ' + senderAddress + '\nTo: ' + str(
                rcpttoData[8:]) + '\nMessage:\n' + str(dataData) + '\n'
            print(userEmail)

            # get email addresses from RCPT TO data
            recUsers = rcpttoData.split(':')
            recUsers = recUsers[1]
            recUsers = recUsers.split()

            # this does the rest of the work
            handleEmailSending(senderAddress, recUsers, userEmail, DOMAIN, otherServers)

    # in server mode, no need for auth or validateUser
    elif userType == 'server':
        heloData = helo(conn)
        senderAddress = mailfrom(conn)
        rcpttoData = rcptto(conn)
        dataData = data(conn)

        userEmail = 'Date: ' + str(datetime.datetime.now()) + '\nFrom: ' + senderAddress + '\nTo: ' + str(
            rcpttoData[8:]) + '\nMessage:\n' + str(dataData) + '\n'
        print(userEmail)

        # get email addresses from RCPT TO data
        recUsers = rcpttoData.split(':')
        recUsers = recUsers[1]
        recUsers = recUsers.split()

        # this does the rest of the work
        handleEmailSending(senderAddress, recUsers, userEmail, DOMAIN, otherServers)

if __name__ == "__main__":
    createDBifNeeded()
    DOMAIN, SELF_IP, SMTP_PORT, HTTP_PORT, otherServers = readFromConf()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servSock:
        servSock.bind(('', int(SMTP_PORT)))
        servSock.listen(5)
        print("server is running...")
        #different parameters for know servers versus users
        while True:
            conn, addr = servSock.accept()
            if addr[0] in otherServers:
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
