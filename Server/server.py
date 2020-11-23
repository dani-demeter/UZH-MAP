from http.server import *
import socketserver
import pickle
from scapy.all import *
PORT = 3005
#Handler = http.server.SimpleHTTPRequestHandler


def pi(filename,packets):
    outfile = open(filename,'wb')
    pickle.dump(packets,outfile)
    outfile.close()
    
class myHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        ip =  self.path[8:]
        print(ip)
        packets =  sniff(timeout=5,filter =f'dst host {ip}')
        filename = 'sniff'
        print(self.path)
        filename = filename + ip
        pi(filename,packets)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        #self.send_header("Content-length", len(b))
        self.end_headers()
        self.wfile.write('HELLO'.encode())
        infile = open(filename,'rb')
        new_dict = pickle.load(infile)
        print(new_dict)
        infile.close()


with socketserver.TCPServer(("", PORT), myHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
