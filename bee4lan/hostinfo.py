# get hosts hostname, IP and MAC address
# MAC by Oren Tirosh
# http://code.activestate.com/recipes/578277-get-mac-address-of-current-interface-in-one-line-o/

import socket
import re, uuid

print socket.gethostname()
print socket.gethostbyname(socket.gethostname())
print ':'.join(re.findall('..', '%012x' % uuid.getnode()))

# this gets MAC for specified ethernet interface
# by Leonid Vasilyev and the same link
# print ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])


# -------------------------------
# https://pymotw.com/2/platform/
# - urcite pridat do zdroju!!
# - zde skvele popsano, jake vystupy budou pro jednotlive systemy: WINDOWS, LINUX, DARWIN(=Apple)

import platform

print
print 'SYSTEM:', platform.system()
# print 'node     :', platform.node()
print 'release:', platform.release()
print 'version:', platform.version()
print 'machine:', platform.machine()
print 'processor:', platform.processor()
print platform.uname()
print
print 'PYTHON:', platform.python_version()
print 'Compiler:', platform.python_compiler()
print 'Build:', platform.python_build()
