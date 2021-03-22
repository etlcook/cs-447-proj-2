SERVER INFO:

Running the server-driver.py script will prompt the user to enter 1, 2, or 3 on the command line, explaining the different options
If there are two instances of the linux terminal, one can run the SMTP-server.py and the other can run the HTTP-server.py
and they can run concurrently.

If the client doesn't communicate well with the server, and It doesnt exit properly, just press 'ctrl + c' and you'll be brought back to the options menu.

CLIENT INFO:

Running client-driver.py will give the user the options to READ, SEND, or QUIT.
READ will open the HTTP client and SEND will open the SMTP client.
If any process gets hung up, try entering QUIT or 'ctrl + c' to close

CONFIGURATION FILES:

the server.conf should look like:
SMTP_PORT=25
HTTP_PORT=80

the client.conf shoudl look like:
SERVER_IP=192.168.0.10
SERVER_PORT=25
HTTP_PORT=80