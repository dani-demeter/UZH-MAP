from scapy.all import *
import pickle
import sys
import pathlib
from threading import Thread


def dumpToFile(filename, packets):
    print(f'Dumping to {filename}')
    outfile = open(filename, 'wb')
    pickle.dump(packets, outfile)
    outfile.close()


def startSniffing():
    ip = ""
    if len(sys.argv) == 2:
        ip = sys.argv[1].replace("::ffff:", "")
        print(f'Destination IP is {ip}')
    filename = pathlib.Path(__file__).parent.absolute() / ("sniff" + str(ip).replace(".", "_").replace(":", "-"))
    print("Starting sniffing")
    packets = sniff(timeout=7, filter=f'dst host {ip}')
    print("Finished sniffing")
    dumpToFile(filename, packets)

    infile = open(filename, 'rb')
    new_dict = pickle.load(infile)
    print(f"The data you collected from {ip} is: {new_dict}")
    infile.close()

startSniffing()
#thread = Thread(target=startSniffing, args=[])
#thread.start()

