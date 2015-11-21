#  udp listener
#
#  Run this in the background, and you will appear to the pipboy app as an instance of Fallout4

import socket
import struct
import sys
import time
import json

# debouncer magic number
min_delta=100

#return current millis
def now():
	return time.time()*1000000
#return millis since 'then'
def dif(then):
	return now() - then
#return true if millis since last_seen is older than minimum debounce interval
def stale(last_seen):
	return ( dif(last_seen) > min_delta )

# set some default globals
multicast_group = '224.3.29.71'
listen_address = ('', 28000)
ttl = struct.pack('b', 127)  # Set the time-to-live for UDP messages.  should be 1.

# here we go

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

# Receive/respond loop
isRunning=True
last_seen = {}
print >>sys.stderr, '\nHANDSHAKE READY...'

while isRunning:
	raw_data, address = hand_sock.recvfrom(1024)
	nodeID = ':'.join(map(str,address))
	print >>sys.stderr, 'HANDSHAKE recieved %d bytes, from: %s' % (len(raw_data), nodeID)
	if not last_seen.get(nodeID):
		print >>sys.stderr, 'HANDSHAKE   new tuple: %s' % nodeID
		last_seen[nodeID] = 0
	if stale(last_seen[nodeID]):
		print >>sys.stderr, 'HANDSHAKE   old timestamp: %d  diff:  %d  stale: %s' % (last_seen[nodeID],dif(last_seen[nodeID]),stale(last_seen[nodeID]))
		udp_msg = json.loads(raw_data)
		if udp_msg['cmd'] == 'autodiscover':
			print >>sys.stderr, 'HANDSHAKE     acknowledging discovery request from %s' % nodeID
			reply = {}
			reply['IsBusy'] = False
			reply['MachineType'] = "PC"
			hand_sock.sendto(json.dumps(reply), address)
		else:
			print >>sys.stderr, 'HANDSHAKE   unrecognized request from %s\nHANDSHAKE content: %s' % (nodeID, udp_msg)
		last_seen[nodeID] = now()
	else:
		print >>sys.stderr, 'HANDSHAKE  ignoring duplicate request from %s' % nodeID





