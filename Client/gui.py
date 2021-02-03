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

        self.frame1 = tk.Frame(
            root, background='#2c2c2c')
        self.frame1.pack(fill='x')

        self.choosePortsLabel = tk.Label(
            self.frame1, text='Choose ports:', font=(None, 20))
        self.choosePortsLabel.grid(row=0, column=0, padx=10, pady=5)

        self.portsEntered = tk.Entry(
            self.frame1, font=(None, 20), text='placeholder', justify=tk.RIGHT)
        self.portsEntered.insert(
            0, "20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 143, 161, 194, 443")
        self.portsEntered.grid(row=0, column=1, padx=10, pady=5)

        self.startMeasurementButton = tk.Button(
            self.frame1, text='Start Measurement', command=self.startMeasurements, font=(None, 25))
        self.startMeasurementButton.grid(row=1, columnspan=2, padx=10, pady=5)
        # self.startMeasurementButton.pack(side=tk.BOTTOM, fill='both')

        self.progressTitle = tk.Label(
            self.root, text='Progress', font=(None, 20))
        self.progressTitle.pack(fill='x')

        self.frame2 = tk.Frame(
            root, background='#2c2c2c')
        self.frame2.pack(fill='x')

        self.progressLabel = tk.Label(
            self.frame2, text="\n", font=('Courier', 12), relief=tk.RIDGE, background='#2c2c2c', foreground='#fff')
        self.progressLabel.pack(side=tk.TOP, fill='x')

        self.logTitle = tk.Label(
            self.root, text="Log", font=(None, 20))
        self.logTitle.pack()

        self.frame3 = tk.Frame(
            root, background='#2c2c2c')
        self.frame3.pack(fill='x')

        self.logLabel = tk.Label(
            self.frame3, text="\n\n\n\n", font=(None, 12), relief=tk.RIDGE, background='#2c2c2c', foreground='#fff')
        self.logLabel.pack(side=tk.TOP, fill='x')

        # self.label.pack(ipadx=4, padx=4, ipady=4, pady=4, fill='both')

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

        print()
        self.startMeasurementButton['state'] = 'disabled'
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
                # self.quit()
                return
            else:
                incomingMessage = line.decode("utf-8")
                if incomingMessage.startswith('('):
                    separatedMessage = incomingMessage[1:-3].split('/')
                    separatedMessage = list(
                        map(lambda x: int(x), separatedMessage))
                    progressbar = "["+separatedMessage[0]*"==" + \
                        (separatedMessage[1]-separatedMessage[0]-1)*"  "+"]"
                    print(progressbar)
                    print(separatedMessage)
                    self.progressLabel['text'] = progressbar
                else:
                    if self.logLabel['text'].count('\n') >= 4:
                        firstLineEnd = self.logLabel['text'].find('\n')
                        self.logLabel['text'] = self.logLabel['text'][firstLineEnd+1:]
                    self.logLabel['text'] += '\n' + \
                        incomingMessage[:-1]  # update GUI
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
