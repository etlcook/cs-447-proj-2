#This is the client for HTTP requests

import socket
import os
import base64
import sys

#make db folder if not exists
path = os.getcwd()
path = path + '/db'
if not os.path.exists(path):
    os.mkdir(path)

#pull data from the client.conf file
config = open('client.conf', 'r')
configValues = config.read()
configList = configValues.split('\n')
SERVER_IP = configList[0]
HTTP_PORT = configList[2]
delim = '='
SERVER_IP = SERVER_IP.split(delim, 1)[1]
HTTP_PORT = HTTP_PORT.split(delim, 1)[1]
print('server IP: ', SERVER_IP, ' on port ', HTTP_PORT, '\n\n')
config.close()

# save to local db
def saveEmails(username, resp):
    userPath = os.getcwd()
    userPath = userPath + '/db/' + username
    if not os.path.exists(userPath):
        os.makedirs(userPath)
        k = open(userPath + '/nextnum.txt', 'w')
        k.write(str(int(1)))
        k.close()

    #split every email up by the message counter, which is only needed when response prints
    emailList = resp.split('Message:') 
    del emailList[0]
    #this for loop creates a new email file for every index in emailList
    for e in emailList:
        nextnumFile = open(userPath + '/nextnum.txt', 'r')
        nextnum = int(nextnumFile.read())
        newFileName = str(nextnum)
        nextnum = nextnum + 1
        nextnumFile.close()
        
        nextnumFile = open(userPath + '/nextnum.txt', 'w')
        nextnumFile.write(str(nextnum))
        nextnumFile.close()

        newEmailFile = open(userPath + '/' + newFileName + '.email', 'w')
        newEmailFile.write(e)
        newEmailFile.close()

def sendGet(username, cliSock):

    numNewEmails = cliSock.recv(1024).decode()
    print('number of unread emails: ' + numNewEmails)
    if numNewEmails == '0':
        print('no emails to be read at this time, have a nice day..')
        cliSock.close()
        sys.exit()

    numEmails = input('enter the number of emails you\'d like to retrieve(or QUIT to quit): ')
    req = ''
    if numEmails == 'QUIT':
        print("quitting, have a nice day\n")
        sys.exit()

    ###generate GET response###
    req = 'GET /db/' + username + ' HTTP/1.1\n'
    req = req + 'Host: ' + SERVER_IP + '\n'
    req = req + 'Count: ' + str(numEmails)

    sendOK = input("\n" + req + '\nsend message? (y/n)')
    if sendOK == 'y':
        cliSock.sendall(bytes(req, 'utf-8'))
        resp = cliSock.recv(1024).decode()
        print('from server:\n', resp)
        if resp[0] == '4':
            print("something went wrong, exiting")
            cliSock.close()
            os.system("python client-driver.py")
            sys.exit()

        saveEmails(username, resp)

    #go back to driver menu
    cliSock.close()
    os.system("python client-driver.py")
    sys.exit()

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliSock:
        cliSock.connect((SERVER_IP, int(HTTP_PORT)))
        print('connection successful\n\n')

        user = input("username: ")
        username = user.encode()
        username = base64.b64encode(username)
        cliSock.sendall(username)
        data = cliSock.recv(1024)
        respCode = data.decode()[0:3]
        # if new user
        if respCode[0:3] == '330':
            data = data.decode()[4:]
            data = data.encode()
            data = base64.b64decode(data)
            data = data.decode()
            print('from server:\n' + '330 ' + data)
            print('new account created and password given, closing..')
            cliSock.close()
            os.system("python client-driver.py")
            sys.exit()

        # if existing user
        elif respCode[0:3] == '334':
            print('from server:\n' + data.decode())
            while True:
                password = input("password: ")
                password = password.encode()
                password = base64.b64encode(password)
                cliSock.sendall(password)
                resp = cliSock.recv(1024).decode()
                if resp[0:3] == '235':
                    sendGet(user, cliSock)
                elif resp[0:3] == '536':
                    cliSock.close()
                    os.system("python client-driver.py")
                    sys.exit()




