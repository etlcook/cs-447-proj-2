#this will run the appropriate script

import os
import sys

while True:
    scriptToRun = input("Would you like to send an email or read your emails?\n type SEND, READ, or QUIT: ")

    if scriptToRun == 'SEND':
        os.system('python SMTP-client.py')
    elif scriptToRun == 'READ':
        os.system('python  HTTP-client.py')
    elif scriptToRun == 'QUIT':
        sys.exit()
    else:
        print('I\'m not sure what you mean, try again...\n')


