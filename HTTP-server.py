#this is the HTTP server

import os
import socket

#pull data from the server.conf file
config = open('server.conf', 'r')
configValues = config.read()
configList = configValues.split('\n')
HTTP_PORT = configList[1]
delim = '='
HTTP_PORT = HTTP_PORT.split(delim, 1)[1]
print('HTTP port: ', HTTP_PORT, '\n')
config.close()


HOST = '192.168.0.10'

emailsLeft = 0
emailCount = 0
userPath = os.getcwd()

#this will manipulate the request string to get needed data
def processGet(req):

    reqLines = req.splitlines()
    line1 = reqLines[0].split()
    line3 = reqLines[2].split()

    global userPath
    userPath = userPath + line1[1]
    global emailCount
    global emailsLeft
    emailCount = int(line3[1])
    emailsLeft = int(line3[1])
    
    #this makes sure the user has a database directory
    if os.path.exists(userPath):
        return True
    else:
        return False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servSock:
    servSock.bind(('', int(HTTP_PORT)))
    servSock.listen()
    print('server is running...')
    conn, addr = servSock.accept()
    with conn:
        print('connected by: ', addr)
        req = conn.recv(1024).decode()
        while True:
            #this function decides if the data is usable
            if processGet(req):
                #get list of filenames minus nextnum.txt
                filenames = os.listdir(userPath)
                filenames.remove('nextnum.txt')
                emailObjects = []
                while emailsLeft > 0:
                    #iter starts at 0 and increments, file is each file in filenames
                    #everything is appended to emailObj
                    iter = emailCount - emailsLeft
                    emailStr = 'Message: ' + str(iter + 1) + '\n'
                    file = open(userPath + '/' + str(filenames[iter]), 'r')
                    emailStr = emailStr + str(file.read())
                    emailObjects.append(str(emailStr))
                    file.close()

                    emailsLeft = emailsLeft - 1

            else:
                resp = '404 directory not found'
                conn.sendall(bytes(resp, 'utf-8'))
                conn.close()
                break

            resp = 'HTTP/1.1 200 OK\nServer: ' + HOST + '\nCount: ' + str(emailCount) + '\nContent-Type: text/plain\n'
            
            #add all email objects to the response string
            for email in emailObjects:
                resp = resp + email

            #send the HTTP response
            conn.sendall(bytes(resp, 'utf-8'))

#go back to server options menu
os.system('server-driver.py')
            

#TODO send files line by line as bytes
