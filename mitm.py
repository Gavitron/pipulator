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
listen_address = ('', 28000)
server_address = ('', 27000)
remote_address = ('192.168.42.101', 27000)
multicast_group = '224.3.29.71'
ttl = struct.pack('b', 8)  # 1 won't leave the network segment

# shared state to tear down udp
isRunning = Value('b', True)

# debouncer magic number
min_delta=100

# just the binary bootstrap payload isolated elsewhere
gestalt_file = 'gestalt.bin'


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
    	return content_file.read()


# define the udp listener thread
def listener(name):
    # Create the socket
    hand_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to the server address
    hand_sock.bind(listen_address)
    hand_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    hand_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print >>sys.stderr, '\nHANDSHAKE: READY...'
    # Receive/respond loop
    last_seen = {}
    while isRunning:
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
            print >>sys.stderr, 'HANDSHAKE: ignoring udp spam from %s' % nodeID

	# close out the socket, we're done here.
	handshake_sock.close()
	isRunning=False

# Main block starts here
if __name__ == '__main__':
	# kick off the udp listener process
    handshake = Process(target=listener, args=(isRunning))
    handshake.start()

	# Create a TCP/IP socket for the listener port
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Create another TCP/IP socket so we can connect to the remote end later.
	remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Start the server Listening for incoming connections
	print >>sys.stderr, 'SERVER   : starting up on %s port %s' % server_address
	server_sock.bind(server_address)
	server_sock.listen(1)

	while isRunning:
	    # Wait for a connection
	    print >>sys.stderr, 'SERVER   :   waiting for a connection'
	    client_sock, client_address = server_sock.accept()

	    # the client connected, so make a connection to the server now
	    try:
	        print >>sys.stderr, 'SERVER   :  connection from', client_address
	        print >>sys.stderr, 'CLIENT   :  connecting to %s port %s' % remote_address
	        remote_sock.connect(remote_address)

	        # Basically just pump the data each way, and tell us what moves through
	        while isRunning:
	            app_msg = remote_sock.recv(5)
	            if app_msg:
	            	app_len = struct.unpack('>Q', app_msg[:4])
	            	if app_len > 0
	            		app_payload = remote_sock.recv(app_len)
	            		app_msg+=app_payload
	                print >>sys.stderr, 'SERVER   :   sent %d bytes, code: %r' % (app_len, app_msg[4])
	                client_sock.sendall(app_msg)
	                # do something here with app_payload
	            else:
	                print >>sys.stderr, 'SERVER   :  hangup from server'
	                isRunning = False
	            serv_msg = client_sock.recv(5)
	            if serv_msg:
	            	serv_len = struct.unpack('>Q', serv_msg[:4])
	            	if serv_len > 0
	            		serv_payload = remote_sock.recv(serv_len)
	            		serv_msg+=serv_payload
	                print >>sys.stderr, 'CLIENT   :   sent %d bytes, code: %r' % (serv_len, serv_msg[4])
	                remote_sock.sendall(serv_msg)
	                # do something here with serv_payload
	            else:
	                print >>sys.stderr, 'CLIENT   :  hangup from client ', client_address
	                isRunning = False

	    finally:
	        # close out the connections
	        print >>sys.stderr, 'SRV/CLI  : closing sockets'
	        isRunning = False
	        connection.close()
	        remote_sock.close()

	print >>sys.stderr, 'SRV/CLI  : reaping children'
    handshake.join()
	print >>sys.stderr, 'SRV/CLI  : done'
