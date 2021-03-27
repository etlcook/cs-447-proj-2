#this is the HTTP server

import os
import sys
import socket
import threading

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

    print('HTTP port: ', HTTP_PORT, '\n')
    config.close()
    return DOMAIN, SMTP_PORT, HTTP_PORT, otherServers

#this will manipulate the request string to get needed data
def processGet(conn, req):

    reqLines = req.splitlines()
    line1 = reqLines[0].split()
    line3 = reqLines[2].split()
    if line1[0] != "GET":
        badReq(conn)

    userPath = os.getcwd()
    userPath = userPath + line1[1]
    try:
        emailCount = int(line3[1])
        emailsLeft = int(line3[1])
    except:
        badReq()
    
    #this makes sure the user has a database directory
    if os.path.exists(userPath):
        return True, userPath, emailCount, emailsLeft
    else:
        return False, 0, 0

def badReq(conn):
    conn.sendall("400 bad GET request, closing..".encode())
    sys.exit()

def main(servSock, conn, addr, DOMAIN):
    # try:
    req = conn.recv(1024).decode()
    # this function decides if the data is usable
    pathExists, userPath, emailCount, emailsLeft = processGet(conn, req)
    if pathExists:
        # get list of filenames minus nextnum.txt
        filenames = os.listdir(userPath)
        filenames.remove('nextnum.txt')
        if len(filenames) < emailCount:
            badReq(conn)
        emailObjects = []
        while emailsLeft > 0:
            # iter starts at 0 and increments, file is each file in filenames
            # everything is appended to emailObj
            iter = emailCount - emailsLeft
            emailStr = 'Message: ' + str(iter + 1) + '\n'
            file = open(userPath + '/' + str(filenames[iter]), 'r')
            emailStr = emailStr + str(file.read())
            emailObjects.append(str(emailStr))
            file.close()

            emailsLeft = emailsLeft - 1

    else:
        resp = '404 directory not found. exiting..'
        conn.sendall(resp.encode())
        sys.exit()

    resp = 'HTTP/1.1 200 OK\nServer: ' + socket.gethostname() + '\nCount: ' + str(
        emailCount) + '\nContent-Type: text/plain\n'

    # add all email objects to the response string
    for email in emailObjects:
        resp = resp + email

    # send the HTTP response
    conn.sendall(resp.encode())

    # except:
    #     conn.sendall("400 something went wrong, closing...".encode())
    #     sys.exit()

if __name__ == "__main__":
    DOMAIN, SMTP_PORT, HTTP_PORT, otherServers = readFromConf()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servSock:
        servSock.bind(('', int(HTTP_PORT)))
        servSock.listen()
        print('server is running...')
        while True:
            conn, addr = servSock.accept()
            print('connected by: ', addr)
            try:
                x = threading.Thread(target=main,
                                     args=(servSock, conn, addr, DOMAIN))
                x.start()
            except threading.error as e:
                print(str(e))
                print('closing from threading exception..')
                sys.exit()

#go back to server options menu
os.system('python server-driver.py')
