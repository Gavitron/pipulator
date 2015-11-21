
import socket
import struct
import sys
import json

# internet variables
tcp_address = ('', 27000)  # listen on all interfaces on the default port
#tcp_address = ('127.0.0.1', 27001)  # a hack so that I can use the tcpserver when testing the mitm proxy.
isRunning = True
gestalt_file = 'captures/gestalt2.bin'   # just the binary bootstrap payload isolated elsewhere

app_info = {
    'lang' : 'en',
    'version' : '1.1.30.0'
}
######
# misc helper function declarations

# one-shot file ingestion
def grok(filename):
    with open(filename, 'r') as content_file:
        whole = content_file.read()
    return whole

######
# build a byte string for tx on the wire
def msg_builder(code=0,payload=''):
    return struct.pack('<LB', len(payload),code)+payload

######
# Main block starts here

# Create a TCP/IP socket for the listener port
game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Start the server Listening for incoming connections
print >>sys.stderr, 'SERVER   : starting up on %s port %s' % tcp_address
game_socket.bind(tcp_address)
game_socket.listen(1)

while isRunning:
    # Wait for a connection
    print >>sys.stderr, 'SERVER   :   waiting for a connection'
    client_socket, client_address = game_socket.accept()
    # the client connected, so make a connection to the server now
    try:
        print >>sys.stderr, 'SERVER   :  connection from', client_address
        # Basically just blat out the raw data without question, just like the real server.
        client_socket.sendall(msg_builder(1,json.dumps(app_info)+'\n'))
        client_socket.sendall(msg_builder(3,grok(gestalt_file)))
        # now we idle in the heartbeat loop forever:
        while isRunning:
            payload = ''
            message = client_socket.recv(5)
            if message:
                msg_len = struct.unpack('<LB', message)
                if msg_len[0] > 0:
                    payload = client_socket.recv(msg_len[0])
                    print >>sys.stderr, 'MESSAGE  :   recv %d bytes, code %r, payload == %s' % (msg_len[0], msg_len[1],payload)
                # we could do stuff here with the inbound messaging.

                # now we compose a reply.
                client_socket.sendall(msg_builder())    # defaults get us the usual heartbeat response
            else:
                print >>sys.stderr, 'MESSAGE   :  error from socket'
                isRunning = False

    finally:
        # close out the connections
        print >>sys.stderr, 'SRV/CLI  : closing sockets'
        isRunning = False
        client_socket.close()

game_socket.close()
print >>sys.stderr, 'SRV/CLI  : done'
