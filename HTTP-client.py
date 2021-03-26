#This is the client for HTTP requests

import socket
import os

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

#this username will be used to generate the GET request
global username 
username = input("username: ")

def saveEmails(resp):
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

def sendGet():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliSock:
        cliSock.connect((SERVER_IP, int(HTTP_PORT)))
        print('connection successful\n\n')
        while True:
            numEmails = input('enter the number of emails you\'d like to retrieve(or QUIT to quit): ')
            req = ''
            if numEmails == 'QUIT':
                cliSock.sendall(numEmails.encode())
                resp = cliSock.recv(1024).decode()
                print('from server-> ', resp)
                exit()
            
            ###generate GET response###

            req = 'GET /db/' + username + ' HTTP/1.1\n'
            req = req + 'Host: ' + SERVER_IP + '\n'
            req = req + 'Count: ' + str(numEmails)

            sendOK = input("\n" + req + '\nsend message? (y/n)')
            if sendOK == 'y':
                cliSock.sendall(bytes(req, 'utf-8'))
                resp = cliSock.recv(1024).decode()
                print('from server->\n', resp)

                saveEmails(resp)

sendGet()

#TODO create directory for emails and save them
