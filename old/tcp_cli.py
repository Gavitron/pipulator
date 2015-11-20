import socket
import sys

server_address = ('192.168.42.101', 27000)
message = '\x00\x00\x00\x00\x00'

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
# Send data
#    print >>sys.stderr, 'sending "%r"' % message
#    sock.sendall(message)

 # Receive the data from the server, and display/interpret it.
    while True:
        data = sock.recv(1024)
        if data:
            print >>sys.stderr, 'received "%r"' % data
            if data == message:
                print >>sys.stderr, 'sending ack'
                sock.sendall(message)
            else:
                #print >>sys.stderr, 'sending "%r"' % message
                print >>sys.stderr, 'sending ack'
                sock.sendall(message)
        else:
            print >>sys.stderr, 'hangup from server'
            break

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()