import threading
import socket
import RPi.GPIO as GPIO
import time
from tkinter import *
import os




    
def onWeightUp():
    global iGoalLbs
    
    if iGoalLbs < 128:
        iGoalLbs += 1
    lblWeightValue.configure(text=str(iGoalLbs))
    PREW_string()

def onWeightDown():
    global iGoalLbs
    
    if iGoalLbs > 1:
        iGoalLbs -= 1
    lblWeightValue.configure(text=str(iGoalLbs))
    PREW_string()

def onSetUp():
    global iGoalSet
    
    if iGoalSet < 10:
        iGoalSet += 1
    lblSetValue.configure(text=str(str(iGoalSet)))
    PREW_string()

def onSetDown():
    global iGoalSet
    
    if iGoalSet > 1:
        iGoalSet -= 1
    lblSetValue.configure(text=str(str(iGoalSet)))
    PREW_string()
    
def onRepUp():
    global iGoalRep
    
    if iGoalRep < 10:
        iGoalRep += 1
    lblRepValue.configure(text=str(iGoalRep))
    PREW_string()

def onRepDown():
    global iGoalRep
    
    if iGoalRep > 1:
        iGoalRep -= 1
    lblRepValue.configure(text=str(iGoalRep))
    PREW_string()





def distance(f, SessionID):
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
    if distance > 100:
        distance = -1
    else:
        arrDistData.append(str(time.time()) +','+ str(distance) +','+ str(SessionID))
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
    f = open(dataPath + '/' + fileSessionData, 'r')
    SessionID = 0
    for line in f.readlines():
        SessionID += 1
    f.close()
    f = open(dataPath + '/' + fileSessionData, 'a')
    f.write(str(SessionID)+','+ UserID + str(time.time()))
    f.close()
                
    f = open(dataPath +'/'+ fileWoData, 'a')
    
    tmrStart = time.time()
    tmrEnd = time.time()
    
    #check that bar is at bottom
    while b1:
        dist=distance(f, SessionID)
        
        if dist > 50:
            b1 = False
    
    bRun = True
    while bRun:
        tmrStart = time.time()
        #state where we are going up
        while b2:
            dist = distance(f, SessionID)
            if dist < 30 and dist != -1:
                b2 = False
                print('b2 false')
        
        #stuff oto do at the top
                
        #state where you are going down
        while not b2:
            dist = distance(f, SessionID)
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
        
        WOIP_string()
    for row in arrDistData:
        f.write('\n' + row)
    f.close()
    
    
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
    
    ##Setup SessionFile
    
    
    
    
    
    
    
    
    
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
    
    thread_woInProg = threading.Thread(target=woInProg)
    thread_woInProg.daemon = True
    thread_woInProg.start()
    
    WOIP_string()

##-------------------------------------------------
##Communications Methods
    
def startAccThread():
    accThread = threading.Thread(target=acceptor)
    accThread.daemon = True
    accThread.start()

def acceptor():
    global userName
    global password
    global bRun
    global iGoalLbs
    global iGoalSet
    global iGoalRep
    global UserID
    global UserName
    global FirstName
    
    while True:
        bLogin = True
        bConn = False
        global conn
        
        ##Waiting for a connection
        c, a = sock.accept()
        conn = [c, a]
        print(str(a[0]) + ':' + str(a[1]), "connected")
        
        ##waits for login information
        
        while True:
            data = c.recv(1024).decode('utf-8')
            print(data)
            if not data:
                print('data length is 0')
                c.close()
                break
            
            elif data == 'DISC=':
                print('disconnected')
                UserID = -1
                UserName = 'n/a'
                FirstName= 'n/a'
                c.close()
                break
            
            if data.find('LOGI=') != -1:
                f = open(dataPath + '/' + fileUserLogin, 'r')
                userInfo = (data.split('=')[1]).split(',')
                if len(userInfo) > 1:
                    for line in f.readlines():
                        print(userInfo[0])
                        print(line.split(',')[1])
                        if userInfo[0].lower() == line.split(',')[1].lower():
                            print(userInfo[1])
                            print(line.split(',')[2])
                            if userInfo[1] == line.split(',')[2]:
                                c.send(('LOGI=' + line).encode('utf-8'))
                                UserID, UserName, Password, FirstName = line.split(',')
                                time.sleep(0.1)
                                PREW_string()
                            else:
                                c.send(b'LOGI=incorrect password')
                        else:
                            c.send(b'LOGI=user not found')
                else:
                    c.send(('LOGI=' + f.read()[int(userInfo[0])]).encode('utf-8'))
                
            elif data.find('NEWU=') != -1:
                i = 0
                bWrite = True
                f = open(dataPath + '/' + fileUserLogin, 'r')
                userInfo = (data.split('=')[1]).split(',')
                print(userInfo)
                for line in f.readlines():
                    print(line)
                    if userInfo[0].lower() == line.split(',')[1].lower():
                        c.send(b'NEWU=user exists')
                        bWrite = False
                        break
                    i += 1
                if bWrite:
                    f.close()
                    f = open(dataPath +'/'+ fileUserLogin, 'a')
                    f.write('\n'+ str(i) + ',' + userInfo[0] + ',' + userInfo[1] + ',' + userInfo[2])
                    c.send(('NEWU='+str(i)).encode('utf-8'))
                f.close()
            elif data.find('BTTN=') != -1:
                if data == 'BTTN=Wup':
                    print('i Goal Lba: ' + str(iGoalLbs))
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
            elif data.find('WOIP=') != -1:
                pass
            else:
                c.send(b'EROR=No expected')
                    
                    
            

def PREW_string():
    print(('PREW=' + str(iGoalLbs) + ',' + str(iGoalSet) + ',' + str(iGoalRep)))
    try:
        conn[0].send(('PREW=' + str(iGoalLbs) + ',' + str(iGoalSet) + ',' + str(iGoalRep)).encode('utf-8'))
    except:
        print('no connection')

def WOIP_string():
    print(('WOIP=' + str(iCurLbs) + ',' + str(iCurSet) + ',' + str(iCurRep)))
    try:
        conn[0].send(('WOIP=' + str(iCurLbs) + ',' + str(iCurSet) + ',' + str(iCurRep)).encode('utf-8'))
    except:
        print('no connection')
        
##-------------------------------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 12343))
sock.listen(1)
startAccThread()
conn = []
    

##File IO variables and setupo
dataPath = './data'
fileUserLogin = 'UserLogin.txt'
fileWoPlans = 'WoPlans.txt'
fileSessionData = 'SessionData.txt'
fileWoData = 'WoData.txt'

if not os.path.isdir(dataPath):
    os.mkdir(dataPath)
    print('Creating ./data folder...')
    
try:
    f = open(dataPath + '/' + fileUserLogin, 'r')
    print('File for UserLogin was found.')
except FileNotFoundError:
    print('File for UserLogin not found. Creating new file...')
    f = open(dataPath + '/' + fileUserLogin, 'w')
    
try:
    f = open(dataPath + '/' + fileSessionData, 'r')
    print('File for UserLogin was found.')
except FileNotFoundError:
    print('File for UserLogin not found. Creating new file...')
    f = open(dataPath + '/' + fileSessionData, 'w')

try:
    f = open(dataPath + '/' + fileWoPlans, 'r')
    print('File for WoPlans was found.')
except FileNotFoundError:
    print('File for WoPlans not found. Creating new file...')
    f = open(dataPath + '/' + fileWoPlans, 'w')

try:
    f = open(dataPath + '/' + fileWoData, 'r')
    print('File for WoData was found.')
except FileNotFoundError:
    print('File for WoData not found. Creating new file...')
    f = open(dataPath + '/' + fileWoData, 'w')

#User Variables
UserID = '-1'
UdserName = 'n/a'
FirstName= 'n/a'

#Wordout variables
arrDistData = []


##GPIO variables
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


lblLeftHead = Label(leftFrame, text='Left', font='Times 36')
lblLeftHead.pack()
lblCenterHead = Label(centerFrame, text='Center',font='Times 36')
lblCenterHead.pack()
lblRightHead = Label(rightFrame, text='Right', font='Times 36')
lblRightHead.pack()



btnStart = Button(centerFrame, text='Start', font='Times 24', command=onStart)

btnWeightUp = Button(leftFrame, text='UP', font='Times 24', command=onWeightUp)
lblWeightValue = Label(leftFrame, text=str(iGoalLbs), font='Times 24')
btnWeightDown = Button(leftFrame, text='DOWN', font='Times 24', command=onWeightDown)

btnSetUp = Button(centerFrame, text='UP', font='Times 24', command=onSetUp)
lblSetValue = Label(centerFrame, text=str(iGoalSet), font='Times 24')
btnSetDown = Button(centerFrame, text='DOWN', font='Times 24', command=onSetDown)

btnRepUp = Button(rightFrame, text='UP', font='Times 24', command=onRepUp)
lblRepValue = Label(rightFrame, text=str(iGoalRep), font='Times 24')
btnRepDown = Button(rightFrame, text='DOWN', font='Times 24', command=onRepDown)


lblWeight = Label(leftFrame, text='lblWeight', font='Times 24')
lblSet = Label(leftFrame, text='lblSet', font='Times 24')
lblRep = Label(leftFrame, text='lblRep', font='Times 24')


initTK()




lblDistance = Label(rightFrame, text='Distance: ##', font='Times 24')

##btnUp.configure(command=onUp)
##btnDown.configure(command=onDown)


win.geometry('800x600')
win.protocol("WM_DELETE_WINDOW", cleanup)
win.mainloop()
