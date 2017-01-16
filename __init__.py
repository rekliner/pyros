#/usr/bin/env python3
import serial
import io
import sys
import glob
from Tkinter import *
import json
import os.path
from pyros import *
#this needs to have a serial port selector    

def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class erosInitWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent        
        parent.wm_title("Eros Connection")
        parent.geometry("120x300+0+0")  
        self.exitButton = Button( parent, text="Quit",command=self.quit,bg="red", fg="white").pack(side="top",anchor="ne")
        status = StatusBar(self)
        status.pack(side=BOTTOM, fill=X)
        self.comSelector = Listbox(parent, height=4)
        self.comSelector.pack()
        self.displayWindow = None
        self.button = Button(parent, text="Refresh", command=self.comRefresh,bg="blue", fg="white").pack()
    counter = 0
    def create_window(self):
        self.counter += 1
        self.displayWindow = Toplevel(self)
        self.displayWindow.geometry("900x600+140+0")  
        self.displayWindow.comPort = str(self.comSelector.get(self.comSelector.curselection()[0]))
        self.displayWindow.wm_title("Eros on %s" % self.displayWindow.comPort)
        l = Label(self.displayWindow, text="This is window #%s" % self.counter)
        l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        self.displayWindow.protocol('WM_DELETE_WINDOW', self.removeWindow)
        self.displayWindow.focus_set()
        self.eros = Pyros()
        self.eros.comPortName = self.displayWindow.comPort
        self.displayWindow.button = Button(self.displayWindow, text="Connect", command=self.eros.erosConnect,bg="blue", fg="white").pack()
        self.displayWindow.button = Button(self.displayWindow, text="ping", command=self.eros.ping,bg="blue", fg="white").pack()
        
    def removeWindow(self):
        if self.eros.comPort != None:
            self.eros.comPort.close()
        self.displayWindow.destroy()
        self.displayWindow = None
        
    def onScale(self, val):
        v = int(float(val))
    def quit(self):
        self.parent.destroy()
        
    def comRefresh(self):
        #load a list of serial ports, display as a list
        if self.comSelector.size() != 0:
            self.comSelector.delete(0, END)
        listSerials = serial_ports()
        for comPort in listSerials:
            self.comSelector.insert(END,comPort)
        #self.comSelector.pack()

class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()    

        
def main():
    root = Tk()
    ex = erosInitWindow(root)
    
    
    #print(var)
    #load preferences/mod file
    prefsPath = "prefs.txt"
    if os.path.isfile(prefsPath):
        f = open(prefsPath,'r+')
        ex.prefs = json.load(f)
        print("loading from prefs file")
    else:
        print("creating new prefs file")
        f = open(prefsPath,'a')
        ex.prefs = json.loads('{"mod":0}')
        json.dump(ex.prefs, f)
    f.close()
    print (json.dumps(ex.prefs))
    print ("mod=" + str(ex.prefs[u'mod']) + "\n")
    f = open(prefsPath,'r+')
    json.dump(ex.prefs, f)
    f.close()
    
    #load the list of comports
    ex.comRefresh()
    
    #default to comport in prefs if there
    selectedPorts = ex.comSelector.curselection()
    if 'comPort' in ex.prefs:
        print("comport in prefs")
        if ex.comSelector.size() > 0:
            for comPort in range(0,ex.comSelector.size()):
                if ex.comSelector.get(comPort) == ex.prefs[u'comPort']:
                    print("comport matches list")
                    ex.comSelector.selection_set(comPort)

    #main loop
    while True:
        #check on prerequisites first:
        #if a comport is actually selected
        if len(ex.comSelector.curselection()) != 0:
            #if serial port selection has changed
            if selectedPorts != ex.comSelector.curselection():
                selectedPorts = ex.comSelector.curselection()
                
                #update the preferences file
                ex.prefs[u'comPort'] = ex.comSelector.get(ex.comSelector.curselection()[0])
                f = open(prefsPath,'r+')
                json.dump(ex.prefs, f)
                f.close()
            
                #if a window for that com already exists it's expired - close it
                if ex.displayWindow != None:
                    ex.removeWindow()
                ex.create_window() #open the control window for the newly selected COM
                
            #comports are all settled and ready, lets talk to the Eros:
            #if not connected
                #connect to ex.displayWindow.comPort
                #read stored eros mod
                #attempt to get bytes from Eros
                #try stored mod, then 0 mod
            #else connected - MAIN FUNCTIONALITY
                #load up a window with the sliders for that mode
                #display values
                #display modes as tabs
                #allow for a "customize mode" window
                #allow to save custom modes as additional tabs?
                #do i need to have a seperate update command for this window? yes.
        root.update_idletasks()
        root.update()
		
if __name__ == '__main__':
    main()  
        