#  synthesize all 3 fragments into one monolith app.
#
#  first, send a UDP broadcast, and locate a fallout game.
#  then spawn a background thread that listens on udp 28000, and replies to app hails as another game
#  when someone connects to me, reach out to the located game, and mitm both sides of the connection, while displaying the data stream

import socket
import sys

# init some vars

server_address = ('', 27000)
remote_address = ('192.168.42.101', 27000)
message = '\x00\x00\x00\x00\x00'
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


# Create a TCP/IP socket for the listener port
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create another TCP/IP socket so we can connect to the remote end later.
remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Start the server Listening for incoming connections
print >>sys.stderr, 'starting up on %s port %s' % server_address
server_sock.bind(server_address)
server_sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    client_sock, client_address = server_sock.accept()

    # the client connected, so make a connection to the server now
    try:
        print >>sys.stderr, 'connection from', client_address
        print >>sys.stderr, 'connecting to %s port %s' % remote_address
        remote_sock.connect(remote_address)

        # Basically just pump the data each way, and tell us what moves through
        while True:
            app_msg = remote_sock.recv(102400)
            if app_msg:
                print >>sys.stderr, 'SERVER: %r' % app_msg
                client_sock.sendall(app_msg)
            else:
                print >>sys.stderr, 'hangup from server'
                break
            serv_msg = client_sock.recv(102400)
            if serv_msg:
                print >>sys.stderr, 'CLIENT: %r' % serv_msg
                remote_sock.sendall(serv_msg)
            else:
                print >>sys.stderr, 'hangup from client ', client_address
                break

    finally:
        # close out the connections
        print >>sys.stderr, 'closing sockets'
        connection.close()
        remote_sock.close()

print >>sys.stderr, 'done'
