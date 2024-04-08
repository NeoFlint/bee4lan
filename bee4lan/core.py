# -*- coding: utf-8 -*-
"""
Core program for bee4lan LAN managing program. 
2016-03 by Flintstone 
...as a part of graduate axamination at www.vosplzen.cz

Bee4lan works simply on basis of text files stored on server. This enables multiple ways of control:
  1. directly editing .txt files
  2. using bee4lan core program in commandline
  3. via graphical environment intended to be created in the future
You can choose which one seems to be most handy for you. 
Many thanks for comments!
"""


import os
import sys
import io
import argparse


# 1 item in hosts: [hostnumber, hostname, OSgroup, usergroup, [info from hostname's file]]
hosts = []
# 1 pair in usergroups: {name of usergroup: [particular hostnames]}
usergroups = {}
# 1 pair in osgroups: {name of osgroup: [particular hostnames]} 
osgroups = {'winXP':[], 'win7':[], 'win10':[]}
# targets = list of hostnames to deploy a script
targets = []
# 1 pair in scripts: {filetype: [list of these available scripts]}
scripts = {}


# paths:
program_path = 'R:\\bee4lan\\'
hosts_path = program_path + 'hosts/'
groups_path = program_path + 'groups/'
scripts_path = program_path  # + 'scripts/'
logs_path = program_path + 'logs/'
history_path = program_path + 'history/'


def readHosts(hosts_path, groups_path):
    """Read all available hosts by means of their info files in hosts_path folder. 
    For working properly, please let make the hostinfo.py script as a first one 
    on a new host. This adds your machine into the bee4lan."""
    
    hosts = []
    usergroups = {}
    global osgroups
    
    # building a list for a host
    for filename in os.listdir(hosts_path):
        tmphost = []
        tmpinfo = []
        tmphost.append(filename.rstrip('.txt'))
        with open(hosts_path + filename, 'r') as f:
            for line in f: 
                tmpinfo.append(line.rstrip("\n")) # read all lines from host's infofile
            f.close()
            
        # in case of other OSs this should be checked and modified
        if tmpinfo[5] == 'release: XP': 
            tmphost.append('winXP')
            osgroups['winXP'].append(tmpinfo[0])
        elif tmpinfo[5] == 'release: 7': 
            tmphost.append('win7')
            osgroups['win7'].append(tmpinfo[0])
        elif tmpinfo[5] == 'release: 10': 
            tmphost.append('win10')
            osgroups['win10'].append(tmpinfo[0])
        else:
            print "An unknown operating sytem found among your hosts!"
        
        tmphost.append(tmpinfo)    
        hosts.append(tmphost) 
       
    # assign something like id number to each host
    hosts.sort()
    for i in range(len(hosts)):
        hosts[i].insert(0,i)
    
    # reading usergroups
    for filename in os.listdir(groups_path): 
        groupname = filename.rstrip('.txt')
        with open(groups_path + filename, 'r') as f:
            content = f.read().split("\n")
            f.close()
        usergroups[groupname] = content
    
    # making usergroup sign to all of hosts
    for host in hosts:
        for key, value in usergroups.items():
            if host[1] in value:
                host.insert(3, key)
                
        # assigning 'all' group to host, if it doesn't belong to any other group
        if type(host[3]) is list:
            host.insert(3, 'all')
    
    return hosts, usergroups, osgroups


def readScripts(scripts_path):
    """Read all available scripts in your scripts_path. Please, maintain only 
    fully functional scripts in this folder. Making them is up to you. Please, remember: this 
    program will be just as handy as your scripts are."""
    
    scripttypes = ['.py','.bat','.cmd','.vbs']
    noscripts = ['todo.bat','control.cfg','core.py','bee4lan_svc.py']
    scripts = {} 
    
    for extension in scripttypes:
        scripts[extension] = []

    for filename in os.listdir(scripts_path):
        extension = os.path.splitext(filename)[1]
        
        # scripts[extension] list should not contain anything from noscripts (important when scripts_path = program_path) 
        if extension in scripttypes: 
            if filename not in noscripts: 
                scripts[extension].append(filename)
    
    # lining up scripts for each filetype
    for key in scripts.keys(): 
        scripts[key].sort()
    
    return scripts
    

def printHosts_Raw(hosts):
    """List hosts with numbers, however, without any sorting."""
    
    print "\n\tYOUR HOSTS:"
    print "\nNumber - name - groups:"
    print "------------------------------"
    for j in range(len(hosts)):
        print hosts[j][0], "-", hosts[j][1], " " * (15-len(hosts[j][1])), "- "+hosts[j][2]+", "+hosts[j][3]
    print "------------------------------"
    print "Number of hosts currently:", len(hosts)
    return
    

def printUserGroups(hosts, usergroups):
    """Prints all groups which you declared using .txt files in the groups_path.
    Please remember: every single hostname can belong only to one group. 
    (Maybe in the future this feature will be changed.)"""

    print "\n\tUSER DEFINED GROUPS:"
    for key in sorted(usergroups.keys()):
        print "\n-------- " + key + " (" + str(len(usergroups[key])) + " hosts) --------"
        for host in usergroups[key]:
            print host 
    return

    
def printScripts(scripts):
    """Prints available scripts sorted by their filetype."""

    print "\n\tYOUR SCRIPTS:"
    for key in sorted(scripts.keys()):
        print "\n-------- " + key + " (" + str(len(scripts[key])) + " scripts) --------"
        for script_name in scripts[key]:
            print script_name
    return


def createTask(newtasknum):
    """Takes all the hostnames from targets list, clears control.cfg file and 
    rewrites it using these hostnames. It includes also new task number, which 
    will be the same as in the todo.bat file.
    
    Since control.cfg is newly stored, all hosts added into bee4lan can make their 
    tries executing what is in todo.bat file."""
    
    print
    try:
        with open(program_path + 'control.cfg', 'w') as f:
            f.write(str(newtasknum))
            f.write("\n")
            for t in targets:
                f.write(t)
        f.close()
        print "Control.cfg created."
    except Exception as e:
        print "ERROR:", repr(e)

    
def createToDo(tasknum, command):
    """Takes given scriptname to deploy, created command from generateCommand function
    and inserts it into newly created todo.bat file.
    All next will be done due to bee4lan service installed on hosts."""

    try:
        with open(program_path + 'todo.bat', 'w') as f: 
            f.write('@echo off\n')
            f.write('REM task ' + str(tasknum) + '\n\n') # ERROR s poctem argumentu - Python spatne pocita, nemohu predat cislo ulohy :-(
            f.write(command)
        f.close()
        print "Todo.bat created."
        
    except Exception as e:
        print "ERROR:", repr(e)


def createNewLog(newtasknum, command):
    """Makes new log file when new task is performed. 
    Bee4lan uses logfiles to know which number should have the next task.
    To reset this line, just delete all files from logs_path 
    directory on server.
    CONSIDER: All hosts has also their own logfiles. Hosts only execute tasks
    with task numbers greater than what they can find in their local logs_path 
    directory.
    """

    try:
        with open(history_path + str(newtasknum) + '.txt', 'w') as f:  
            f.write(str(newtasknum)+'\n')
            f.write(command)
            f.write("\n\n") # vytvori jednoradkovou mezeru
            for t in targets:
                f.write(t)
        f.close()
        print "New log file created."
    except Exception as e:
        print "ERROR:", repr(e)
    
    
def generateCommand(a_execute):
    """Prepares a command for executeScript() function depending on script's extension."""

    global scripts
    
    ext = os.path.splitext(a_execute)[1]
    
    comm = ''
    if a_execute.endswith('.py'):
        comm = 'python.exe ' + scripts_path + a_execute
    elif a_execute.endswith('.bat' or '.cmd'):
        comm = scripts_path + a_execute
    elif a_execute.endswith('.vbs'):
        comm = 'cscript ' + scripts_path + a_execute
    else:
        print "ERROR: Your script type is not supported!"
        sys.exit()
    
    # replacing all slashes with backslashes as the .bat script needs 
    comm = comm.replace('/', '\\')
    return comm


def argsToTargets(a_targets):
    """Analyses args giving by -t option in commandline and decompose them into 
    particular hostnames on which the given script by -x option will be performed.
    
    As args you can use usergroup names, osgroup names and numbers of your hosts.
    'all' ... the script will be deployed to all of them."""
   
    global hosts, usergroups, osgroups, targets
    tmptargets = []
    
    # in case of group 'all' was used
    if 'all' in a_targets:
        for h in hosts:
            targets.append(h[1])
        targets.sort()
        return targets
    
    # in other cases - mixed input is also possible
    for tt in a_targets:
        if isInt(tt): # a number entered
            try:                 
                tmptargets.append(hosts[int(tt)][1])
            except Exception as e:
                print "ERROR: Unknown host number entered!"
                sys.exit()
        else:
            for key, value in osgroups.items(): # osgroup entered
                if tt == key:
                    tmptargets.extend(value)
                    break
                    
            for key, value in usergroups.items(): # usergroup entered
                if tt == key:
                    tmptargets.extend(value)
                    break
    
    # building targets[] without any duplicit hostnames
    for t in tmptargets:
        if t not in targets: targets.append(t)
    targets.sort()
    
    return targets


def isInt(num):
    """Find out if the given string is convertible into int or not."""

    try:
        int(num)
        return True
    except:
        return False

        
def executeScript(a_targets, a_execute):
    """Main function controlling new task execution.
    It prints all information to user and waits for confirmation before new task 
    is performed.
    
    Other function called from here:
        createToDo(newtasknum, command)
        createTask(newtasknum)
        createNewLog(newtasknum, command)
    """
    
    global scripts
    
    history = []
    for filename in os.listdir(history_path):
        history.append(int(filename.rstrip('.txt')))
    
    history.sort()
    if len(history) == 0 or history[-1] < 100:
        print "\n!!! ATTENTION !!! \nServer task history found empty. Next task number is 101."
        print "Hosts could need empty their history also to work again!"
        newtasknum = 101
    else:
        newtasknum = int(history[-1] + 1)
    
    print '\n',' '*15, "YOUR TASK ("+ str(newtasknum)+"):\n", '-'*40
    command = generateCommand(a_execute)
    print command
        
    print '\n',' '*15, "TO HOSTS:\n", '-'*40
    # prints all hosts for deploying the script
    for t in argsToTargets(a_targets.split(',')):
        print t
    
    # caution before execution - waiting for confirmation from admin user
    print '\n','-'*40
    answer = raw_input("Control.cfg and todo.bat file will be overwritten. \nDo you want to continue [y/n]?: ")
    if answer in ('y','Y','yes','YES'):

        # calling additional functions...
        createToDo(newtasknum, command)
        createTask(newtasknum)
        createNewLog(newtasknum, command)
    
    else:
        print "Exiting..."
        sys.exit()
    
    return

        
def setDelay(delay):
    """Basic delay is implemented on the side of client - 10s in main loop of 
    bee4lan service. However, it depends on when the host started his loop.
    This feature is intended for next version of bee4lan."""

    print("ERROR: Oh, no! I'm sorry, I don't have set up this function yet...")
    return


def message_and_exit(message):
    """Additional function for processing inputs from commandline."""

    print message
    sys.exit()
    
    
        
# -------------------------- MAIN: -----------------------------
def main():
    """Main function of bee4lan core program. It is used for recognition if 
    the whole program or if you just want to use some parts of it."""
    
    global hosts, usergroups, osgroups
    hosts, usergroups, osgroups = readHosts(hosts_path, groups_path)
    global scripts
    scripts = readScripts(scripts_path)

    parser = argparse.ArgumentParser(description='Bee4lan main controlling program for Windows hosts at LAN. You can do it via your own scripts, which you just prepared to deploy on hosts and placed into scripts folder. Be well, John Spartan!')
    parser.add_argument('-x','--execute', help='Which script you want to execute', required=False, default=None)
    parser.add_argument('-t','--targets', help='Target hosts to launch your script. You can give numbers as follows: 1,2,3,8,9,10,12. You can also give names of your groups and you - of course - can mix both. If you dont use this option, the script will be launched on all your computers. CAUTION: If you use this option, control.cfg and todo.bat files will be overwritten with new generated data!',required=False)
    parser.add_argument('-d','--delay', help='Delay before the script will be launched on your computers specified in option -t.',required=False, default=0)
    parser.add_argument('-l','--listhosts', help="Lists all avilable hosts which you can control. If you want to edit them manualy, go to the 'hosts' folder.", action='store_true')
    parser.add_argument('-s','--showscripts', help="Show list of your available scripts in 'scripts' folder.", action='store_true')
    parser.add_argument('-g','--showusergroups', help="Show list of user defined groups. You can create and edit groups in 'groups' folder. Each .txt file is your group. It enables you to handle hosts your way.", action='store_true')

    if len(sys.argv) == 1:
        sys.argv += ["-h"]

    args = parser.parse_args()

    if args.execute:
        if args.targets is None:
            message_and_exit("\nERROR: Targets or execution script not specified. Use both -x and -t option. Or you can specify your task directly into control.cfg and todo.bat.file!")
        if args.execute not in os.listdir(scripts_path):
            message_and_exit("\nERROR: Script '" + args.execute + "' is not in your scripts folder or does not exist.")
            
        # all 'execute' options are correctly given
        executeScript(args.targets, args.execute)
        message_and_exit("")
            
    elif args.targets:
        message_and_exit( "\nERROR: Bad syntax. Please, se -h for help."  )

    # === other args handling: ===
    if args.showusergroups: 
        printUserGroups(hosts, usergroups)
    if args.showscripts: 
        printScripts(scripts)
    if args.listhosts: 
        printHosts_Raw(hosts)
    if args.delay: 
        setDelay(args.delay)


# -------------------------- STARTING PROGRAM -----------------------------
if __name__ == "__main__":
   main()
    