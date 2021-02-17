#!/usr/bin/python
"""
- read output from a subprocess in a background thread
- show the output in the GUI
"""
import sys
from itertools import islice
from subprocess import Popen, PIPE
from textwrap import dedent
from threading import Thread
import subprocess
import os
from ast import literal_eval as make_tuple
import json

try:
    import Tkinter as tk
    from Queue import Queue, Empty
except ImportError:
    import tkinter as tk  # Python 3
    from queue import Queue, Empty  # Python 3


def iter_except(function, exception):
    try:
        while True:
            yield function()
    except exception:
        return


class MAPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title = 'Net Neutrality Breach Tool'
        # root.state('zoomed')

        # MEASUREMENT
        self.startMeasurementTitle = tk.Label(
            self.root, text='Start a measurement', font=(None, 20))
        self.startMeasurementTitle.bind(
            "<Button-1>", lambda x: self.frame_measurement.pack_forget() if bool(self.frame_measurement.winfo_ismapped()) else self.frame_measurement.pack(after=self.startMeasurementTitle, fill='x'))
        self.startMeasurementTitle.pack(fill='x')

        self.frame_measurement = tk.Frame(
            root, background='#2c2c2c')
        self.frame_measurement.pack(fill='x')

        self.choosePortsLabel = tk.Label(
            self.frame_measurement, text='Choose ports:', font=(None, 20))
        self.choosePortsLabel.grid(
            sticky="W", row=0, column=0, padx=10, pady=10)

        self.portsEntered = tk.Entry(
            self.frame_measurement, font=(None, 20), text='placeholder', justify=tk.RIGHT)
        self.portsEntered.insert(
            0, "20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 143, 161, 194, 443")
        self.portsEntered.grid(sticky="E", row=0, column=1, padx=10, pady=10)

        self.startMeasurementButton = tk.Button(
            self.frame_measurement, text='Start Measurement', command=self.startMeasurements, font=(None, 25))
        self.startMeasurementButton.grid(row=1, columnspan=2, padx=10, pady=10)

        self.frame_measurement.grid_rowconfigure(0, weight=1)
        self.frame_measurement.grid_columnconfigure(0, weight=1)

        # BOUNTY
        self.bountyTitle = tk.Label(
            self.root, text='Place a Bounty', font=(None, 20))
        self.bountyTitle.bind(
            "<Button-1>", lambda x: self.frame_bounty.pack_forget() if bool(self.frame_bounty.winfo_ismapped()) else self.frame_bounty.pack(after=self.bountyTitle, fill='x'))
        self.bountyTitle.pack(fill='x')

        self.frame_bounty = tk.Frame(
            root, background='#2c2c2c')
        self.frame_bounty.pack(fill='x')

        self.bounty_types = ["Distance", "Ping", "ISP"]
        self.bounty_type = tk.StringVar(self.frame_bounty)
        self.bounty_type.set(self.bounty_types[0])
        self.bounty_type_chooser = tk.OptionMenu(
            self.frame_bounty, self.bounty_type, *self.bounty_types)
        self.bounty_type_chooser.config(
            font=(None, (20)), background='#2c2c2c', foreground="#fff")
        self.bounty_type_chooser.grid(
            sticky="W", row=0, column=0, padx=10, pady=10)

        self.bountyValue = tk.Entry(
            self.frame_bounty, font=(None, 20), justify=tk.RIGHT)
        self.bountyValue.grid(sticky="E", row=0, column=1, padx=10, pady=10)

        self.bountyRepeatsLabel = tk.Label(
            self.frame_bounty, text='Number of measurements:', font=(None, 20))
        self.bountyRepeatsLabel.grid(
            sticky="W", row=1, column=0, padx=10, pady=10)

        self.bountyRepeatsBox = tk.Entry(
            self.frame_bounty, font=(None, 20), justify=tk.RIGHT)
        self.bountyRepeatsBox.insert(
            0, "1")
        self.bountyRepeatsBox.grid(
            sticky="E", row=1, column=1, padx=10, pady=10)

        self.bountyAmountLabel = tk.Label(
            self.frame_bounty, text='Bounty amount per measurement (pwei):', font=(None, 20))
        self.bountyAmountLabel.grid(
            sticky="W", row=2, column=0, padx=10, pady=10)

        self.bountyAmountBox = tk.Entry(
            self.frame_bounty, font=(None, 20), justify=tk.RIGHT)
        self.bountyAmountBox.insert(
            0, "1")
        self.bountyAmountBox.grid(
            sticky="E", row=2, column=1, padx=10, pady=10)

        self.placeBountyButton = tk.Button(
            self.frame_bounty, text='Place Bounty', command=self.placeBounty, font=(None, 25))
        self.placeBountyButton.grid(row=3, columnspan=2, padx=10, pady=10)

        self.frame_bounty.grid_rowconfigure(0, weight=1)
        self.frame_bounty.grid_columnconfigure(0, weight=1)

        # PROGRESS
        self.progressTitle = tk.Label(
            self.root, text='Progress', font=(None, 20))
        self.progressTitle.bind(
            "<Button-1>", lambda x: self.frame2.pack_forget() if bool(self.frame2.winfo_ismapped()) else self.frame2.pack(after=self.progressTitle, fill='x'))
        self.progressTitle.pack(fill='x')

        self.frame2 = tk.Frame(
            root, background='#2c2c2c')
        self.frame2.pack(fill='x')

        self.progressLabel = tk.Label(
            self.frame2, text="\n", font=('Courier', 12), relief=tk.RIDGE, background='#2c2c2c', foreground='#fff')
        self.progressLabel.pack(side=tk.TOP, fill='x')

        # LOG
        self.logTitle = tk.Label(
            self.root, text="Log", font=(None, 20))
        self.logTitle.bind(
            "<Button-1>", lambda x: self.frame3.pack_forget() if bool(self.frame3.winfo_ismapped()) else self.frame3.pack(after=self.logTitle, fill='x'))
        self.logTitle.pack(fill='x')

        self.frame3 = tk.Frame(
            root, background='#2c2c2c')
        self.frame3.pack(fill='x')

        self.logLabel = tk.Label(
            self.frame3, text="\n\n\n\n", font=(None, 12), relief=tk.RIDGE, background='#2c2c2c', foreground='#fff')
        self.logLabel.pack(side=tk.TOP, fill='x')

        # self.label.pack(ipadx=4, padx=4, ipady=4, pady=4, fill='both')

    def placeBounty(self):
        bountyType = self.bounty_type.get()
        bountyReq = self.bountyValue.get()
        bountyNumRep = self.bountyRepeatsBox.get()
        bountyVal = self.bountyAmountBox.get()
        print(bountyType, bountyReq, bountyNumRep, bountyVal)
        self.startMeasurementButton['state'] = 'disabled'
        self.placeBountyButton['state'] = 'disabled'
        self.process = Popen(['python', os.path.dirname(
            os.path.abspath(__file__))+'/SmartContractTest.py', 'placeBounty', str(bountyType), str(bountyReq), str(bountyNumRep), str(bountyVal)], stdout=PIPE)
        q = Queue(maxsize=1024)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True  # close pipe if GUI process exits
        t.start()
        self.update(q)  # start update loop

    def startMeasurements(self):
        ports = make_tuple(self.portsEntered.get())
        validPorts = ()
        for port in ports:
            try:
                portInt = int(port)
                if(portInt < 0 or portInt > 65353):
                    print("Not a port in range")
                else:
                    validPorts += (port, )
            except ValueError:
                print("Not an int")

        self.startMeasurementButton['state'] = 'disabled'
        self.placeBountyButton['state'] = 'disabled'
        self.process = Popen(['python', os.path.dirname(
            os.path.abspath(__file__))+'/test.py', str(validPorts)], stdout=PIPE)
        q = Queue(maxsize=1024)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True  # close pipe if GUI process exits
        t.start()
        self.update(q)  # start update loop

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        try:
            with self.process.stdout as pipe:
                for line in iter(pipe.readline, b''):
                    q.put(line)
        finally:
            q.put(None)

    def update(self, q):
        """Update GUI with items from the queue."""
        for line in iter_except(q.get_nowait, Empty):  # display all content
            if line is None:
                if hasattr(self, 'process'):
                    self.process.kill()
                self.startMeasurementButton['state'] = 'normal'
                self.placeBountyButton['state'] = 'normal'
                # self.quit()
                return
            else:
                incomingMessage = json.loads(line.decode("utf-8"))
                if incomingMessage['tag'] == 'progress':
                    progressbar = "[" + incomingMessage['completed']*"==" + (
                        incomingMessage['total'] - incomingMessage['completed'] - 1)*"  " + "]"
                    # separatedMessage = incomingMessage[1:-3].split('/')
                    # separatedMessage = list(
                    #     map(lambda x: int(x), separatedMessage))
                    # progressbar = "["+separatedMessage[0]*"==" + \
                    #     (separatedMessage[1]-separatedMessage[0]-1)*"  "+"]"
                    # print(progressbar)
                    # print(separatedMessage)
                    self.progressLabel['text'] = progressbar
                elif incomingMessage['tag'] == 'log':
                    if self.logLabel['text'].count('\n') >= 4:
                        firstLineEnd = self.logLabel['text'].find('\n')
                        self.logLabel['text'] = self.logLabel['text'][firstLineEnd+1:]
                    self.logLabel['text'] += '\n' + \
                        incomingMessage['message']  # update GUI
                break  # display no more than one line per 40 milliseconds
        self.root.after(40, self.update, q)  # schedule next update

    def quit(self):
        if hasattr(self, 'process'):
            self.process.kill()
        self.root.destroy()


root = tk.Tk()
app = MAPGUI(root)
root.protocol("WM_DELETE_WINDOW", app.quit)
root.mainloop()
