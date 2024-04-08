# -*- coding: utf-8 -*- 
# http://stackoverflow.com/questions/8943371/cant-start-windows-service-written-in-python-win32serviceutil
# Inspiration and supercision: Mgr. Filip Vaculik - Mintaka

# with python 2.7.10 and 2.7.11 works well

# Installation:
# -------------
# 1. install python 2.7.10 or 2.7.11 and pywin32 (both as admin!)- be sure that 
#    versions do match and that you used original .exe installators
# 2. register python services (in admin's cmd!) with
#
#       C:\Python27\Lib\site-packages\win32\pythonservice.exe /register
#
# 3. use this python scripts with it's proper usage below

# Usage:
# ------
# python bee4lan.py --startup auto install
# python bee4lan.py start
# python bee4lan.py stop
# python bee4lan.py remove
# ...controlling via windows "sc" commands is also possible

import win32serviceutil
import win32service
import win32event
import win32api
import logging
import time
import os, sys
import subprocess
from shutil import copyfile

class Bee4lan(win32serviceutil.ServiceFramework):
    """Bee4lan CLASS."""
    
    _svc_name_ = "bee4lan"
    _svc_display_name_ = "bee4lan"  # name for msconfig
    _svc_description_ = "Bee4lan is a service for managing LAN computers by LAN admins"

    def __init__(self, *args):
        """Init function of this class."""
        
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.COMPUTER_NAME = os.environ['COMPUTERNAME']
        self.SERVER_SHARE = "\\\\192.168.1.100\\abs"
        self.SERVER_DIR = "R:/bee4lan/"
        self.LOCAL_DIR = "C:/Program Files/bee4lan/"
        self.CONTROL_FILE = self.SERVER_DIR + "control.cfg"
        self.EXECUTION_FILE = self.SERVER_DIR + "todo.bat"
        self.LOGFILE_GLOBAL = self.SERVER_DIR + "logs/clients_MAIN.log"
        self.LOGFILE_LOCAL = self.LOCAL_DIR + self.COMPUTER_NAME + "_svc.log"
        self.HISTORY_FOLDER = self.LOCAL_DIR + "history/"
        self.CURR_TASK_NUM = 0
        self.LAST_EDIT_TIME = 0
        self.REQ_HOSTS = []  
        self.TIMEOUT = 10 # waiting seconds
        self.logLocal("-------- init done --------")

    def SvcRun(self):
        """Main function with the infinite loop containing all the functionality performed by this service."""
    
        self.logLocal("started")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.mountDrives()



        
        # ---------------- INFINITE LOOP, LOOKING FOR TASKS: ----------------
        while True:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.TIMEOUT)
            if rc == win32event.WAIT_OBJECT_0:
                self.logLocal("stopped")
                self.logGlobal("Bee4lan service STOPPED.")
                break

            self.readReqHostsAndTaskNumber()
            self.checkTasks()
            
            time.sleep(self.TIMEOUT) # wait before you do again
            
        # -------------- ^ INFINITE LOOP, LOOKING FOR TASKS ^ ---------------




    def SvcStop(self):
        """Enables this service to stop from Windows API."""
        
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    
    
    def readReqHostsAndTaskNumber(self):
        """Read a lists of hosts from server, who are intended to perform the task 
        and store this information in the REQ_HOSTS class list."""       
        
        try:
            with open(self.CONTROL_FILE, 'r') as f:
                lines = f.readlines()
                
                self.REQ_HOSTS = []
                for line in lines: 
                    if line == "\n": # empty lines in control.cfg doesn't matter 
                        continue
                    else:
                        self.REQ_HOSTS.append(line.rstrip("\n").lower())  
                
                self.CURR_TASK_NUM = int(self.REQ_HOSTS[0])
                self.REQ_HOSTS = self.REQ_HOSTS[1:]
                #self.logLocal(str(self.REQ_HOSTS))
                
            f.close()
        except:
            self.logLocal("Checking control.cfg on server FAILED!")
        return

    
    def mountDrives(self):
        """Mount network drives needed by this service (SYSTEM account) to work."""
    
        s = win32api.GetLogicalDriveStrings() # vypis pripojenych jednotek pred akci
        self.logLocal('mounted drives: '+ str(s).replace('\\\x00', ' '))
        
        try:
            if "R:" not in s:
                self.launchWithoutConsole("net", ["use", "R:", self.SERVER_SHARE,])
                self.logLocal("Mounting drives, delay 10s...")
                time.sleep(10) # 10s delay for being mounted properly
                s = win32api.GetLogicalDriveStrings() # vypis pripojenych jednotek po akci
                self.logLocal('mounting drives... now mounted: '+ str(s).replace('\\\x00', ' '))
                
                if "R:" not in s:
                    self.logLocal("Mounting server share FAILED!")
                
            self.logGlobal("Bee4lan service STARTED.")
                    
        except Exception as err:
               self.logLocal(repr(err))
                                 
        return
    

    def compareNums(self):   
        """Return True if current task has not been performed yet."""
        
        files = os.listdir(self.HISTORY_FOLDER) # vrati list s nahodnym poradim
        files.sort()
        if len(files) == 0:
            self.logLocal("My task history found empty. Previous task number have been reset to 101.") 
            lastnum = 101 # ulohy maji vzdy cisla > 100
        else: 
            if (files[-1].rstrip(".txt")).endswith("_FAIL"):
                lastnum = int(files[-1].rstrip("_FAIL.txt"))
            else:
                lastnum = int(files[-1].rstrip(".txt")) # zjisti jmeno souboru s nejvyssim cislem, odebere mu koncovku, prevede na int a ulozi do num
            
        message = "CURR_TASK_NUM = "+str(self.CURR_TASK_NUM)+", lastnum = "+str(lastnum) # debug
        self.logLocal(message)        
        # pokud zjisti, ze ulohu jiz delal, vrati False, jinak True
        #self.logLocal(str(self.CURR_TASK_NUM) + ", lastnum:"+ str(lastnum))
        if self.CURR_TASK_NUM <= lastnum: 
            return False
        else:
            return True

    
    def checkTimeChanges(self):
        """Firstly look at time changes of control.cfg. If any were done, you 
        don't have to do anything else.
        This should save some system resources...
        Works since second try from launching the service or from making the task. 
        This behavior is normal."""

        stats = os.stat(self.CONTROL_FILE)
        if self.LAST_EDIT_TIME < time.localtime(stats[8]):
            self.LAST_EDIT_TIME = time.localtime(stats[8])
            self.logLocal("Changes in control.cfg detected.")
            return True
        else:
            return False
    
    
    def checkTasks(self):
        """Check if there is a task on the server to be done."""
        
        # Are there any changes in main control file?
        if self.checkTimeChanges() == False:
            # self.logGlobal (str(self.CURR_TASK_NUM) + " Nothing new") # debug
            return
        
        # Is the task really new? I don't like being stuck in a loop...
        if self.compareNums() == False: 
            self.logGlobal(str(self.CURR_TASK_NUM) + " Task already performed. Skipping task...")
            return
    
        # Is the task intended for me?
        if self.COMPUTER_NAME.lower() not in self.REQ_HOSTS:
            self.logGlobal(str(self.CURR_TASK_NUM) + " Not for me...") 
        else:
            self.logLocal (str(self.CURR_TASK_NUM) + " RUNNING TASK!")
            self.logGlobal (str(self.CURR_TASK_NUM) + " RUNNING TASK!")
            
            
            # >>>>>>> RUNNING task from server!
            p = subprocess.call(self.EXECUTION_FILE, shell=False)
            #p = self.startScript(self.EXECUTION_FILE)
 
            
            # reporting success to server and making local history file
            if p == 0: 
                self.logLocal(str(self.CURR_TASK_NUM) + " Task done successfully!")
                self.logGlobal(str(self.CURR_TASK_NUM) + " Task done successfully!")
                copyfile(self.EXECUTION_FILE, self.HISTORY_FOLDER + str(self.CURR_TASK_NUM) + ".txt")
            else:
                self.logLocal(str(self.CURR_TASK_NUM) + " Task FAILED! returncode = " + str(p))
                self.logGlobal(str(self.CURR_TASK_NUM) + " Task FAILED! returncode = " + str(p))
                copyfile(self.EXECUTION_FILE, self.HISTORY_FOLDER + str(self.CURR_TASK_NUM) + "_FAIL.txt")
        
        return


    def startScript(self, command, start_state = 'SW_SHOWNORMAL'):
        """Launches command with its visible window. Usefull when we do something 
        for user and need his interaction. 
        Set status for new window. See end of script or:
        https://msdn.microsoft.com/en-us/library/ms633548"""
           
        states = {'SW_SHOWMINNOACTIVE': 7, 'SW_HIDE': 0, 'SW_SHOWNORMAL': 1, 'SW_MAXIMIZE': 6}
        start_state = states[start_state]

        SW_HIDE = 0
        proc = subprocess.STARTUPINFO()
        proc.dwFlags = subprocess.STARTF_USESHOWWINDOW
        proc.wShowWindow = start_state
        
        # RUN it!
        subprocess.Popen(command, startupinfo=proc)


    def launchWithoutConsole(self, command, args):
        """Launches 'command' windowless. Usefull when we do something 
        what doesn't need any interaction from user and it is required to not 
        obstruct user during his work.
        SYSTEM = the default user managing bee4lan service and also launching our scripts on clients."""
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        return subprocess.Popen([command] + args, startupinfo=startupinfo,stderr=subprocess.PIPE, stdout=subprocess.PIPE)


    def logGlobal(self, message):
        """Logging function to log on the server."""
        
        try:
            f = open(self.LOGFILE_GLOBAL, 'a')
            f.write(time.strftime('%Y-%m-%d, %H:%M:%S - ')+self.COMPUTER_NAME+' - '+ message +'\n')
            f.close()
        except:
            return
        return
        
    def logLocal(self, message):
        """Logging function to log localy."""
        
        try:
            f = open(self.LOGFILE_LOCAL, 'a')
            f.write(self.COMPUTER_NAME+', '+time.strftime('%H:%M:%S')+' - '+ message +'\n')
            f.close()
        except:
            return
        return

if __name__ == '__main__':
    """A condition which can recognize if this script is used in one piece 
    or if you just use some parts of it."""
    # This enables this service being controlled by Windows API.
    win32serviceutil.HandleCommandLine(Bee4lan)


"""
SHOWING WINDOWS STATUS
https://msdn.microsoft.com/en-us/library/ms633548

Atribute - Value -	Meaning
SW_FORCEMINIMIZE    11 Minimizes a window, even if the thread that owns the window is not responding. This flag should only be used when minimizing windows from a different thread.
SW_HIDE             0 Hides the window and activates another window.
SW_MAXIMIZE         3 Maximizes the specified window.
SW_MINIMIZE         6 Minimizes the specified window and activates the next top-level window in the Z order.
SW_RESTORE          9 Activates and displays the window. If the window is minimized or maximized, the system restores it to its original size and position. An application should specify this flag when restoring a minimized window.
SW_SHOW             5 Activates the window and displays it in its current size and position.
SW_SHOWDEFAULT      10 Sets the show state based on the SW_ value specified in the STARTUPINFO structure passed to the CreateProcess function by the program that started the application.
SW_SHOWMAXIMIZED    3 Activates the window and displays it as a maximized window.
SW_SHOWMINIMIZED    2 Activates the window and displays it as a minimized window.
SW_SHOWMINNOACTIVE  7 Displays the window as a minimized window. This value is similar to SW_SHOWMINIMIZED, except the window is not activated.
SW_SHOWNA           8 Displays the window in its current size and position. This value is similar to SW_SHOW, except that the window is not activated.
SW_SHOWNOACTIVATE   4 Displays a window in its most recent size and position. This value is similar to SW_SHOWNORMAL, except that the window is not activated.
SW_SHOWNORMAL       1 Activates and displays a window. If the window is minimized or maximized, the system restores it to its original size and position. An application should specify this flag when displaying the window for the first time.
"""