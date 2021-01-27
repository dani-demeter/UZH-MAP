from scapy.all import *

send(IP(dst="127.0.0.1")/UDP(dport=8082)/Raw(load="abc"))