#this is what starts the SMTP and HTTP servers

import os

script = input('enter 1 for SMTP\nenter 2 for HTTP\nenter 3 to quit\n')
if script == '1':
    os.system('python SMTP-server.py')
elif script == '2':
    os.system('python HTTP-server.py')
else:
    print('goodbye')
    exit()



