#this will run the appropriate script

import os
import sys

scriptToRun = input("Would you like to send an email or read your emails?\n type SEND, READ, or QUIT: ")

if scriptToRun == 'SEND':
    os.system('python SMTP-client.py')
    sys.exit()
elif scriptToRun == 'READ':
    os.system('python  HTTP-client.py')
    sys.exit()
else:
    sys.exit()



