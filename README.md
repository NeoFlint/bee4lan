BEE4LAN Instructions
====================
2016 by Flintstone
neotramp@gmail.com

Bee4lan application is intended as a tool for network administrators, who 
manage LANs with client computers running Windows. 
An pplication needs only Python, samba network share and a computer.  This 
computer could be a server running Linux (best option), a client windows machine, or 
admin’s own computer at home. 

Bee4lan management system is based on Python 2.7.11 and its extension pywin32.
Use
	python-2.7.11.msi
	pywin32-220.win32-py2.7.exe
if you want have the original environment.
All this stuff you can find at this installation CD. 

Any comments are welcome!


Bee4lan installation to SERVER:
---------------------------------
- simply copy bee4lan folder to your fileserver.
- do it first


Bee4lan installation to a CLIENT:
---------------------------------
- IMPORTANT!!! Set correct paths especially in these files on server:
    
    bee4lan\install\bee4lan_svc.py
    bee4lan\core.py
    setup_svc.bat

- Now go to your client computer. Manually connect your intended server share, open 
administrators command prompt, services.msc and eventvwr.
- run this batchfile on server:
    
    setup_svc.bat
     



If something went wrong, here is what you have to do manually:
--------------------------------------------------------------
0. Set correct paths especially in these files on server:
    
    bee4lan\install\bee4lan_svc.py
    bee4lan\core.py
    setup_svc.bat
    
1. Join manually your client PC to server share, and ensure that you can reach 
bee4lan files on server from your admin's command prompt.
2. Install Python 2.7.11 or 2.7.10
3. Install adequate version of extension pywin32
4. register pythonservice.exe:

    C:\Python27\Lib\site-packages\win32\pythonservice.exe /register
    
5. Install bee4lan service:
    
    up.bat
    
6. Run hostinfo script:

    runHostinfo.bat
    
7. Check services.msc and eventvwr(see applications). If no errors have been 
raised, now you can control your computer from server.
Reboot client manually and check again if everything is ok. That's all!   




Bee4lan uninstallation from CLIENT:
-----------------------------------
- stop bee4lan service
- uninstall it
- remove all files from bee4lan from the path:

    C:\Program Files\bee4lan
    
- or use 

    uninstall_svc.bat

   
Bee4lan uninstallation from SERVER:
-----------------------------------
Remove all files.
