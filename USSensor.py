import multiprocessing
import socket
import RPi.GPIO as GPIO
import time
from tkinter import *




    
def onWeightUp():
    global iGoalLbs
    
    if iGoalLbs < 128:
        iGoalLbs += 1
    lblWeightValue.configure(text=str(iGoalLbs))

def onWeightDown():
    global iGoalLbs
    
    if iGoalLbs > 1:
        iGoalLbs -= 1
    lblWeightValue.configure(text=str(iGoalLbs))

def onSetUp():
    global iGoalSet
    
    if iGoalSet < 10:
        iGoalSet += 1
    lblSetValue.configure(text=str(str(iGoalSet)))

def onSetDown():
    global iGoalSet
    
    if iGoalSet > 1:
        iGoalSet -= 1
    lblSetValue.configure(text=str(str(iGoalSet)))
    
def onRepUp():
    global iGoalRep
    
    if iGoalRep < 10:
        iGoalRep += 1
    lblRepValue.configure(text=str(iGoalRep))

def onRepDown():
    global iGoalRep
    
    if iGoalRep > 1:
        iGoalRep -= 1
    lblRepValue.configure(text=str(iGoalRep))





def distance():
    #Sets TRIGGER to High
    GPIO.output(GPIO_TRIGGER, True)
    
    #Sets TRIGGER to Low
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    BeginTime = time.time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        if StartTime-BeginTime>0.1:
            break
    
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        if StopTime-StartTime>0.1:
            break
    
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    lblDistance.configure(text='Distance: ' + str(round(distance)))
    time.sleep(0.1)
    return distance


def woInProg():
    global iCurSet
    global iCurRep
    global bRun
    
    
    bRun = True
    b1 = True
    b2 = True
    
    tmrStart = time.time()
    tmrEnd = time.time()
    
    #check that bar is at bottom
    while b1:
        dist=distance()
        
        if dist > 50:
            b1 = False
    
    bRun = True
    while bRun:
        tmrStart = time.time()
        #state where we are going up
        while b2:
            dist = distance()
            if dist < 30:
                b2 = False
                print('b2 false')
        
        #stuff oto do at the top
                
        #state where you are going down
        while not b2:
            dist = distance()
            if dist > 50:
                b2 = True
                print('b2 true')
        
        tmrEnd = time.time()
        lblCenterHead.configure(text=str(round(tmrEnd-tmrStart)))
        
        #check if goal
        iCurRep += 1
        if iCurRep > iGoalRep:
            iCurSet += 1
            iCurRep = 1
            if iCurSet > iGoalSet:
                bRun = False
        lblSet.configure(text = 'Set: ' + str(iCurSet))
        lblRep.configure(text = 'Rep: ' + str(iCurRep))
        


def cleanup():
    GPIO.cleanup()
    win.destroy()


def initTK():
    lblLeftHead.configure(text='Weight')
    lblCenterHead.configure(text='Number of sets')
    lblRightHead.configure(text='Number of reps')
    
    btnWeightUp.pack()
    lblWeightValue.pack()
    btnWeightDown.pack()

    btnSetUp.pack()
    lblSetValue.pack()
    btnSetDown.pack()

    btnRepUp.pack()
    lblRepValue.pack()
    btnRepDown.pack()
    
    
    
    btnStart.pack()

def onStart():
    global iCurLbs
    iCurLbs=iGoalLbs
    
    btnStart.destroy()
    
    btnWeightUp.destroy()
    lblWeightValue.destroy()
    btnWeightDown.destroy()

    btnSetUp.destroy()
    lblSetValue.destroy()
    btnSetDown.destroy()

    btnRepUp.destroy()
    lblRepValue.destroy()
    btnRepDown.destroy()
    
    lblLeftHead.configure(text='Details')
    lblCenterHead.configure(text='')
    lblRightHead.configure(text='Debugging')
    
    #into left frame
    lblWeight.pack(anchor=W)
    lblWeight.configure(text='Weight: ' + str(iCurLbs))
    lblSet.pack(anchor=W)
    lblSet.configure(text='Set: ' + str(iCurSet))
    lblRep.pack(anchor=W)
    lblRep.configure(text='Rep: ' + str(iCurRep))
    
    #into right frame
    lblDistance.pack(anchor=W)
    
    thread_woInProg = multiprocessing.Process(target=woInProg)
##    thread_woInProg.daemon = True
    thread_woInProg.start()

##-------------------------------------------------
##Communications Methods
    
def startAccThread():
    accThread = multiprocessing.Process(target=acceptor)
##    accThread.daemon = True
    accThread.start()

def acceptor():
    global userName
    global password
    bLogin = True
    
    
    ##Waiting for a connection
    c, a = sock.accept()
    
    print(str(a[0]) + ':' + str(a[1]), "connected")
    
    ##waits for login information
    while bLogin:
        print('wating for login info...')
        data = c.recv(1024).decode('utf-8')
        print(data)
        if not data:
            print('data length is 0')
            print(str(a[0]) + ':' + str(a[1]), "disconnected")
            startAccThread()
            self.stop()
            
        if data.find('LOGI=') != -1:
            bLogin = False
        elif data.find('NEWU=') != -1:
            bLogin = False
        else:
            c.send(b'EROR=LOGI is expected')
    c.send(b'PREW=')
    ##waits for button commands
    buttonThread = multiprocessing.Process(target=buttonState, args=(c,a))
##    buttonThread.daemon = True
    buttonThread.start()
    while not bRun:
        ##breaks when the workout begins
        pass
    buttonThread.terminate()
    print('buttonThread is now closed (maybe)')

def buttonState(c, a):
    global bRun
    while True:
        print('waiting for button...')
        data = c.recv(1024).decode('utf-8')
        print('*' + data + '*')
        
        if not data:
            print('data length is 0')
            print(str(a[0]) + ':' + str(a[1]), "disconnected")
            startAccThread()
            self.stop()
        
        
        if data.find('BTTN=') != -1:
            if data == 'BTTN=Wup':
                onWeightUp()
            if data == 'BTTN=Wdown':
                onWeightDown()
            if data == 'BTTN=Rup':
                onRepUp()
            if data == 'BTTN=Rdown':
                onRepDown()
            if data == 'BTTN=Sup':
                onSetUp()
            if data == 'BTTN=Sdown':
                onSetDown()
            if data == 'BTTN=Start':
                onStart()
            PREW_string(c)

def PREW_string(c):
    c.send(('PREW=' + str(iGoalLbs) + ',' + str(iGoalSet) + ',' + str(iGoalRep)).encode('utf-8'))
        
        
##-------------------------------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 12343))
sock.listen(1)
startAccThread()
    
    
    
    
GPIO.setmode(GPIO.BOARD)

GPIO_TRIGGER = 38
GPIO_ECHO = 40

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

####Global Variables
iGoalLbs=1
iGoalRep=1
iGoalSet=1
iCurLbs=0
iCurRep=1
iCurSet=1
bRun = True

win = Tk()
##win.geometry("900x600")

leftFrame = Frame(win, borderwidth=10)
leftFrame.pack(side=LEFT, fill=Y)
centerFrame = Frame(win,borderwidth=10)
centerFrame.pack(side=LEFT, fill=Y)
rightFrame = Frame(win, borderwidth=10)
rightFrame.pack(side=LEFT, fill=Y)


lblLeftHead = Label(leftFrame, text='Left', font='Times 24')
lblLeftHead.pack()
lblCenterHead = Label(centerFrame, text='Center',font='Times 24')
lblCenterHead.pack()
lblRightHead = Label(rightFrame, text='Right', font='Times 24')
lblRightHead.pack()



btnStart = Button(centerFrame, text='Start', font='Times 12', command=onStart)

btnWeightUp = Button(leftFrame, text='UP', font='Times 12', command=onWeightUp)
lblWeightValue = Label(leftFrame, text=str(iGoalLbs), font='Times 12')
btnWeightDown = Button(leftFrame, text='DOWN', font='Times 12', command=onWeightDown)

btnSetUp = Button(centerFrame, text='UP', font='Times 12', command=onSetUp)
lblSetValue = Label(centerFrame, text=str(iGoalSet), font='Times 12')
btnSetDown = Button(centerFrame, text='DOWN', font='Times 12', command=onSetDown)

btnRepUp = Button(rightFrame, text='UP', font='Times 12', command=onRepUp)
lblRepValue = Label(rightFrame, text=str(iGoalRep), font='Times 12')
btnRepDown = Button(rightFrame, text='DOWN', font='Times 12', command=onRepDown)


lblWeight = Label(leftFrame, text='lblWeight', font='Times 12')
lblSet = Label(leftFrame, text='lblSet', font='Times 12')
lblRep = Label(leftFrame, text='lblRep', font='Times 12')


initTK()




lblDistance = Label(rightFrame, text='Distance: ##', font='Times 24')

##btnUp.configure(command=onUp)
##btnDown.configure(command=onDown)


win.protocol("WM_DELETE_WINDOW", cleanup)
win.mainloop()
