#  udp listener
#
#  Run this in the background, and you will appear to the pipboy app as an instance of Fallout4

import socket
import struct
import sys

multicast_group = '224.3.29.71'
server_address = ('', 28000)

msg_ping = '{"cmd":"autodiscover"}'
msg_ack  = '{ "IsBusy" : false, "MachineType" : "PipUlator" }'  # MachineType should be "PC" but this appears to make no difference to the app.

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 127)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(1024)

    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data

    print >>sys.stderr, 'sending acknowledgement to', address
    sock.sendto(msg_ack, address)
    #sock.sendto('ack', address)
