from http.server import *
import socketserver
import pickle
from scapy.all import *
import time
PORT = 3005
#Handler = http.server.SimpleHTTPRequestHandler


def pi(filename,packets):
    outfile = open(filename,'wb')
    pickle.dump(packets,outfile)
    outfile.close()


def ping():
    current_time = time.time()
    return str(current_time)


class myHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print('Got request')
        print(self.path)
        if self.path == '/ping':
            result = ping()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(result))
            self.end_headers()
            self.wfile.write(f'{result}'.encode())  
        # ip =  self.path[8:]
        # print(ip)
        # packets =  sniff(timeout=5,filter =f'dst host {ip}')
        # filename = 'sniff'
        # print(self.path)
        # filename = filename + ip
        # pi(filename,packets)
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # #self.send_header("Content-length", len(b))
        # self.end_headers()
        # self.wfile.write('HELLO'.encode())
        # infile = open(filename,'rb')
        # new_dict = pickle.load(infile)
        # print(new_dict)
        # infile.close()


with socketserver.TCPServer(("", PORT), myHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
