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

with open('repl.txt', 'r') as content_file:
    content = content_file.read()

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        rcpt = ''
        has_sent_gestalt = False

        while True:
            data = connection.recv(16)
            print >>sys.stderr, 'received "%s"' % data
            rcpt+=data
            if data:
                if has_sent_gestalt:
                    connection.sendall('\n') 
                else:
                    has_sent_gestalt = True
                    print >>sys.stderr, 'sending gestalt'
                    f = open('repl.txt')
                    connection.sendall(content)

            else:
                print >>sys.stderr, 'hangup from', client_address
                break

    finally:
        # Clean up the connection
        connection.close()