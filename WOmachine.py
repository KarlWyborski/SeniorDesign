#! python3
import socket
import threading
import sys
from datetime import datetime
import time
import tkinter
from tkinter import *
import os
##import Tkinter.font

port = 12345

helv70 = ('Helvetica',70)
helv70B = ('Helvetica Bold',70)
helv30 = ('Helvetica', 30)
##win = Tk()
##helv36 = font.Font(family = 'Helvetica',size = 70)
##helv48B = tkFont.Font(family = 'Helvetica',size = 70, weight = "bold")

#Superclasses
class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    iLbs = 0
    sHistFileName = "/home/pi/DeweysProject/Testing/test.txt"
    
    def __init__(self):
        self.sock.bind(('0.0.0.0', 12345))
        self.sock.listen(1)
        self.startAccThread()

##----------
    def startAccThread(self):
        accThread = threading.Thread(target=self.acceptor)
        accThread.daemon = True
        accThread.start()
    
    def acceptor(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0]) + ':' + str(a[1]), "connected")
    
    def handler(self, c, a):
        while True:
            data = c.recv(1024).decode('utf-8')
            print(data)
            if data == 'CurrentTime':
                
                c.send(str(self.iCurrentTime).encode('utf-8'))
            elif data == 'FullHist':
                c.send((self.sHistTimes[0] + ',' + self.sHistTimes[1] + ',' + self.sHistTimes[2] + ',' + self.sHistTimes[3] + ',' + self.sHistTimes[4]
                       + ',' + self.sHistStamps[0] + ',' + self.sHistStamps[1] + ',' + self.sHistStamps[2] + ',' + self.sHistStamps[3] + ',' + self.sHistStamps[4]).encode('utf-8'))
##                c.send(sHistStamps[0] + ',' + sHistStamps[1] + ',' + sHistStamps[2] + ',' + sHistStamps[3] + ',' + sHistStamps[4])
            else:
                c.send(('I got:' + data).encode('utf-8'))
            if not data:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                c.close()
                break

class Client:
    
    def __init__(self, address):
        self.sRequest = 'PlaceHolder'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipAddress = address
        
        self.startSendThread()
        self.connect()
    
    def sendMsg(self):
        while True:
            
            print(str(threading.active_count()) + 'in send thread')
            try:
                self.sock.send((self.sRequest).encode('utf-8'))
                print('Sending data Request: ' + self.sRequest)
            except BrokenPipeError as e:
                print('BrokenPipeError detected...')
                self.connState = False
                self.sock.close()
                time.sleep(1)
                self.connect()
            time.sleep(1)
    
    def rcvMsg(self):
        while True:
            self.data = self.sock.recv(1024)
            if not self.data:
                break
            print(str(self.data.decode('utf-8')))
            self.data = self.data.decode('utf-8')
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ipAddress, port))
            self.startRcvThread()
            self.connState = True
        except ConnectionRefusedError as e:
            self.sock.close()
            print('Connection Failed. Retrying...')
            print(threading.active_count())
            time.sleep(10)
            self.connect()
    
    def startRcvThread(self):
        rcvThread = threading.Thread(target=self.rcvMsg)
        rcvThread.daemon = True
        rcvThread.start()
        print('Rcv Thread Started.')
    
    def startSendThread(self):
        sendThread = threading.Thread(target=self.sendMsg)
        sendThread.daemon = True
        sendThread.start()
        print('Send Thread Started.')
        
    
        

class Window:
##    win = Tk()
##    leftFrame = Frame(win)
##    leftBottomFrame = Frame(leftFrame)
##    leftLeftFrame = Frame(leftFrame)
##    leftRightFrame = Frame(leftFrame)
##    rightFrame = Frame(win)
##    rightLeftFrame = Frame(rightFrame)
##    rightRightFrame = Frame(rightFrame)
##    clock = Label(leftBottomFrame)
##    lCurrentTime = Label(leftLeftFrame)
    def __init__(self):
        self.win = Tk()
        self.win.geometry("500x500")
        
        self.leftFrame = Frame(self.win)
        self.leftFrame.pack(side=LEFT)
        
        self.rightFrame = Frame(self.win, borderwidth=10)
        self.rightFrame.pack(side=RIGHT)
        
        
        self.lLeftHead = Label(self.leftFrame, text='Weight', font='Times 36')
        self.lLeftHead.pack()
        
        self.bUp = Button(self.leftFrame, text='UP', font='Times 24')
        self.bUp.pack()
        
        self.lWeightValue = Label(self.leftFrame, text='0', font='Times 24')
        self.lWeightValue.pack()
        
        self.bDown = Button(self.leftFrame, text='DOWN', font='Times 24')
        self.bDown.pack()
        
        self.lRightHead = Label(self.rightFrame, text='Sensor Data', font='Times 36')
        self.lRightHead.pack()
        
        self.lVoltage = Label(self.rightFrame, text='Voltage:  ##', font='Times 36')
        self.lVoltage.pack()
        
        self.lCurrent = Label(self.rightFrame, text='Current:  ##', font='Times 36')
        self.lCurrent.pack()
        
        self.lDistance = Label(self.rightFrame, text='Distance: ##', font='Times 36')
        self.lDistance.pack()
        
        



#Subclasses
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
class ServerWindow(Server, Window):
    
    def __init__(self):
        Server.__init__ (self)
        Window.__init__ (self)
        
        self.bUp.configure(command=self.onUp)
        self.bDown.configure(command=self.onDown)
        
        self.win.mainloop()
        
    def onUp(self):
        self.iLbs += 1
        print(self.iLbs)
        self.lWeightValue.configure(text=str(self.iLbs))
    
    def onDown(self):
        self.iLbs += -1
        print(self.iLbs)
        self.lWeightValue.configure(text=str(self.iLbs))
    

    
if (len(sys.argv) > 1):
    if sys.argv[2] == 'small':
        client = SmallClient(sys.argv[1])
    elif sys.argv[2] == 'big':
        client = BigClient(sys.argv[1])
##    client.run()
##elif (len(sys.argv) == 2):
##    client = ClientBig(sys.argv[1])
##    client.run()
else:
    server = ServerWindow()
##    server.run()

