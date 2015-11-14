import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.42.101', 27000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    # Send data
    message = '\x00\x00\x00\x00\x00'
    print >>sys.stderr, 'sending "%r"' % message
    sock.sendall(message)

 # Receive the data in small chunks and retransmit it
    while True:
        data = sock.recv(1024)
        if data:
            print >>sys.stderr, 'received "%r"' % data
        else:
            recv += data

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()