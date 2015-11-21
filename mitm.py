#  synthesize all 3 fragments into one monolith app.
#
#  first, send a UDP broadcast, and locate a fallout game.
#  then spawn a background thread that listens on udp 28000, and replies to app hails as another game
#  when someone connects to me, reach out to the located game, and mitm both sides of the connection, while displaying the data stream

import socket
import struct
import sys
import time
import json

from multiprocessing import Process, Value

# internet variables
#game_address = ('192.168.42.101', 27000)  # the IP/port pair of the PC where FO4 is running.
game_address = ('127.0.0.1', 27001)  # a hack so that I can use the tcpserver when testing.
tcp_address = ('', 27000)   # the local TCP port on which to listen
udp_address = ('', 28000)   # the local UDP port on which to listen

multicast_group = '224.3.29.71'  # something for Multicast UDP
ttl = struct.pack('b', 8)  # 1 won't leave the local network segment
min_delta=100  # magic number for udp debouncer

isRunning = Value('b', True)   # shared state to tear down threads

gestalt_file = 'captures/gestalt.bin'   # just the binary bootstrap payload isolated elsewhere

######
# misc helper function declarations

#return current millis
def now():
    return time.time()*1000000
#return millis since 'then'
def dif(then):
    return now() - then
#return true if millis since last_seen is older than minimum debounce interval
def stale(last_seen):
    return ( dif(last_seen) > min_delta )

# one-shot file ingestion
def grok(filename):
    with open(filename, 'r') as content_file:
        whole = content_file.read()
    return whole

######
# build a byte string for tx on the wire
def msg_builder(code=0,payload=''):
    return struct.pack('<LB', len(payload),code)+payload

# tcp mesage pump to proxy two sockets
def tcp_pump(sockin,sockout):
    payload = ''
    message = sockin.recv(5)
    if message:
        msg_len = struct.unpack('<LB', message)
        if msg_len[0] > 0:
            payload = sockin.recv(msg_len[0])
            message+=payload
        sockout.sendall(message)
        print >>sys.stderr, 'MESSAGE  :   proxied %d bytes, code %r' % (msg_len[0], msg_len[1])
    else:
        print >>sys.stderr, 'MESSAGE   :  error from socket'
        payload = False
    return msg_len[1],payload

######
# define the udp listener thread
def listener(isThreadRunning):
    # Create the socket
    hand_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to the server address
    hand_sock.bind(udp_address)
    hand_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    hand_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print >>sys.stderr, '\nHANDSHAKE: READY...'
    # Receive/respond loop
    last_seen = {}
    while isThreadRunning:
        raw_data, address = hand_sock.recvfrom(1024)
        nodeID = ':'.join(map(str,address))
        print >>sys.stderr, 'HANDSHAKE: recieved %d bytes, from: %s' % (len(raw_data), nodeID)
        if not last_seen.get(nodeID):
            print >>sys.stderr, 'HANDSHAKE:   new tuple: %s' % nodeID
            last_seen[nodeID] = 0
        if stale(last_seen[nodeID]):
            print >>sys.stderr, 'HANDSHAKE:   old timestamp: %d  diff:  %d  stale: %s' % (last_seen[nodeID],dif(last_seen[nodeID]),stale(last_seen[nodeID]))
            udp_msg = json.loads(raw_data)
            if udp_msg['cmd'] == 'autodiscover':
                print >>sys.stderr, 'HANDSHAKE:     acknowledging discovery request from %s' % nodeID
                reply = {}
                reply['IsBusy'] = False
                reply['MachineType'] = "PC"
                hand_sock.sendto(json.dumps(reply), address)
            else:
                print >>sys.stderr, 'HANDSHAKE:   unrecognized request from %s\nHANDSHAKE: content: %s' % (nodeID, udp_msg)
            last_seen[nodeID] = now()
        else:
            print >>sys.stderr, 'HANDSHAKE: ignoring duplicate request from %s' % nodeID

    # close out the socket, we're done here.
    handshake_sock.close()
    isThreadRunning=False

######
# Main block starts here
if __name__ == '__main__':
    # kick off the udp listener process
    handshake = Process(target=listener, args=(isRunning,))
    handshake.start()

    # Create a TCP/IP socket for the listener port, and
    # another so we can connect to the remote end later.
    game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Start the server Listening for incoming connections
    print >>sys.stderr, 'PROXY    : starting up on %s port %s' % tcp_address
    proxy_socket.bind(tcp_address)
    proxy_socket.listen(1)

    while isRunning:
        # Wait for a connection
        print >>sys.stderr, 'PROXY    :   waiting for a connection'
        client_socket, client_address = proxy_socket.accept()

        # the client connected, so make a connection to the server now
        try:
            print >>sys.stderr, 'PROXY    :  connection from', client_address
            print >>sys.stderr, 'PROXY    :  connecting to %s port %s...' % game_address
            game_socket.connect(game_address)

            # Basically just pump the data each way.  Later we should do something with the non-empty return payloads.
            while isRunning:
                directions = [(game_socket,client_socket),(client_socket,game_socket)]
                toggle=False
                for (in, out) in directions:
                    toggle=not toggle
                    if toggle:
                        flow='>'
                    else:
                        flow='<'
                    (code,payload)=tcp_pump(in,out)
                    if code == 1:
                        data=json.loads(payload)
                        print >>sys.stderr, 'PROXY %c  :  app version: %s  lang: %s  ' % (flow,data['version'],data['lang'])
                    elif code == 3:
                        print >>sys.stderr, 'PROXY %c  :  gestalt seen, %d bytes' % (flow,len(payload))
                    else:
                        if payload==False:
                            isRunning = False
                        elif payload!='':
                            print >>sys.stderr, 'PROXY %c  : unknown code %d with %d bytes, ' % (flow,code,len(payload))
        finally:
            # close out the connections
            print >>sys.stderr, 'PROXY    : closing sockets'
            isRunning = False
            client_socket.close()
            game_socket.close()

    print >>sys.stderr, 'PROXY    : reaping children'
    proxy_socket.close()
    handshake.join()
    print >>sys.stderr, 'PROXY    : done'
