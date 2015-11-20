import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('', 27000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

replies = {
    'nullstr' : '\x00\x00\x00\x00\x00',
    'onestr' : '\x00\x0f\x00\x00\x00\x00',
    'fivstr' : '\x05\x9dr\x01\x00\x10\xef\x82A',
    'sixstr' : '\x06\x00\x00\x00\x03',
    'ninstr' : '\x09\x00\x00\x00\x03',
    'twvstr' : '\x12\x00\x00\x00\x03',
}

with open('repl.txt', 'r') as content_file:
    content = content_file.read()

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        # once we crack the data format, this would be a 'hydrate data' moment
        has_sent_gestalt = False
        key = 'nullstr'

        # Receive the data in chunks and display it, wihle keeping the heartbeat going
        while True:
            data = connection.recv(1024)
            print >>sys.stderr, 'received "%r"' % data
            if data:
                if has_sent_gestalt:
                    print >>sys.stderr, 'sending %s' % key
                    connection.sendall(replies[key]) 
                else:
                    has_sent_gestalt = True
                    print >>sys.stderr, 'sending gestalt'
                    connection.sendall(content)

            else:
                print >>sys.stderr, 'hangup from', client_address
                break

    finally:
        # Clean up the connection
        connection.close()