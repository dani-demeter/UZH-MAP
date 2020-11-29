# import client
from scapy.all import *
import pickle
s = pickle.load(open("serverPacketsByClient", 'rb'))
c = pickle.load(open("clientPacketsByClient", 'rb'))


def cleaner(packets):  # removes all ssh files and only shows packets with load
    l = []
    for p in packets:
        if TCP in p:
            if Raw in p:
                if p.sport == 3000:
                    l.append(p)
    return l


s = cleaner(s)
c = cleaner(c)
# use s[1][Raw] to compare
print(type(s[0][Raw]))
print()
print(type(c[1][Raw]))
print()
print(s[0][Raw].payload == c[1][Raw].payload)
