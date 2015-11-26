#  Connect to a known game Server and spew out whatever it tells us, before the missing heartbeat causes us to disco
#

import socket
import struct
import sys
import json

# internet variables
#game_address = ('192.168.42.101', 27000)  # the IP/port pair of the PC where FO4 is running.
game_address = ('127.0.0.1', 27001)  # a hack so that I can use the tcpserver when testing.

######
# misc helper function declarations

######
# build a byte string for tx on the wire
def msg_builder(msg_type=0,contents=''):
    return struct.pack('<LB', len(contents),msg_type)+contents

# generator f'n to take an arbitrary string and pump it through, one byte at a time
def byte_pump(byte_string):
    for byte in byte_string:
        yield byte


######
# Main block starts here

# the client connected, so make a connection to the server now
try:
    print >>sys.stderr, 'CLIENT    :  connecting to %s port %s...' % game_address
    game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_socket.connect(game_address)
    isRunning=True
    while isRunning:
        message = game_socket.recv(5)
        if message:
            (msg_len,code) = struct.unpack('<LB', message)
            if msg_len > 0:
                payload = game_socket.recv(msg_len)
                print >>sys.stderr, 'CLIENT  :   recd %d bytes payload with code %r' % (msg_len, code)
            else:
                payload = False
            if code==0:
                #no-op for heartbeat
                if payload:
                    print >>sys.stderr, 'WARNING, NONZERO PAYLOAD OF %d BYTES IN HEARTBEAT MESSAGE.\n ABORTING RUN AND DUMPING PAYLOAD:\n%u' % \
                                            (msg_len, payload)
                    isRunning=False
                    break
            elif code == 1:
                data=json.loads(payload)
                print >>sys.stderr, 'CLIENT  :  app version: %s  lang: %s  ' % (data['version'],data['lang'])
            elif code == 3:
                print >>sys.stderr, 'CLIENT  :  gamestate update, %d bytes' % len(payload)
            elif code == 5:
                data=json.loads(payload)
                print >>sys.stderr, 'CLIENT  :  unknown JSON state message.  Dumping:\n%s\n\n' % \
                                        json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                print >>sys.stderr, 'CLIENT  :  unknown code "%d", payload of %d bytes ' % (code,len(payload))

            # reply with an empty heartbeat
            game_socket.sendall(msg_builder())
        else:
            print >>sys.stderr, 'CLIENT   :  error from socket'
            isRunning = False
finally:
    # close out the connections
    print >>sys.stderr, 'CLIENT    : closing socket'
    game_socket.close()

