#!/usr/bin/env python
from Tkinter import *
from threading import *
import os,re,time,sys,socket,struct,fcntl,struct

class runnableGUI(Thread):
    def __init__(self,list,value):
        Thread.__init__(self)
        self.list=list
        self.value=value
    def run(self):
        self.list.insert(END,self.value)
                

class createFrame(Thread):
    def __init__(self,parent):
        Thread.__init__(self)
        self.parent=parent
        self.start()
    def run(self):
        self.root=Tk()
        self.root.title("Hosts Scanned")
        self.root.mainloop()
    
    
class runnable(Thread):
	def __init__(self,host):
		Thread.__init__(self)
		self.host=host
		self.status=-1
	def run(self):
		pingedList = os.popen("ping -c1 "+self.host,"r")
		while 1:
		      line = pingedList.readline()
		      if not line: break
		      pingstat = re.findall(runnable.checkString,line) #Check ICMP response
		      if pingstat:
			print "Pinging Host : ",self.host
		         #Display Host only when it is Alive
			if pingstat[0]!="0":
			   	threadGUI=runnableGUI(listbox,self.host) #listbox from mainloop
                                threadGUI.start()
                                threadGUI.join()
		            	self.status=int(pingstat[0])
		
#checkString is a RegEx
runnable.checkString = re.compile(r"(\d) received")

# If OS is not Windows
if os.name != "nt":
    def get_int_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

def get_ip():
    ip = socket.gethostbyname(socket.gethostname()) 	# Works on Windows, not on Linux
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
        for ifname in interfaces: 			# try to get IP address from each interface. When IP found, break from Loop.
                try:
                        ip = get_int_ip(ifname)
                        break;
                except IOError:
                        pass
    return ip

#Print the host's IP address
addr=get_ip()
print "Your IP address is ",addr

#Mask calculation
octets=addr.split('.')
if int(octets[0])<128:
	mask=8
elif int(octets[0])>=128 and octets[0]<192:
	mask=16
else :
	mask=24


# Convert from Octets format to Number format
def quadToNum(ip):
    return struct.unpack('!L',socket.inet_aton(ip))[0]

# Convert from Number format to Octets format
def numToQuad(n):
    return socket.inet_ntoa(struct.pack('!L',n))

# Make the binary form of mask using Mask bits.
def makeMaskBits(n):
    n=32-n
    return (1L<<n)-1

# Find netaddr and hostaddr
def ipToNetAndHost(ip, mask):
    n = quadToNum(ip)
    m = makeMaskBits(mask)
    host = n & m
    net = n - host
    return numToQuad(net), numToQuad(host)

netaddr,hostaddr=ipToNetAndHost(addr,mask)

#The host's network and host address
print "Network Address : ",netaddr,"\nHost Address : ",hostaddr,"\nNetwork Mask : ",mask
print
 
if __name__ == '__main__':
    app=createFrame(None)
    listbox=Listbox()
    scroll=Scrollbar(command=listbox.yview)
    listbox.configure(yscrollcommand=scroll.set)
    listbox.pack(side=LEFT)
    scroll.pack(side=RIGHT,fill=Y)
    hostlist=["1","2","3"]
    '''for host in hostlist:
        threadGUI=runnableGUI(listbox,host)
        threadGUI.start()
        threadGUI.join()
    '''
    
    #Thread List
    threadlist=[]
    
    print "Hosts in LAN"
    #Ping all hosts in network range and detect presence
    for host in (numToQuad(quadToNum(netaddr)+n) for n in range(1, (1<<(32-mask))-2)): #ignore the network address and broadcast address
            thread=runnable(host)
            threadlist.append(thread)
            thread.start()
            
    
    #Maintaining a flag to maintain limited concurrent threads
            waitflag=0
            if len(threadlist)>300:
                    waitflag=1
            if host==254:
                    waitflag=len(threadlist)
    
            if waitflag==1:
                    index=0
                    while index<len(threadlist):
                            check=threadlist[index]
                            if check.status>-1:
                                    check.join(1.0)
                                    del threadlist[index]
                                    waitflag=waitflag-1
                            else:
                                    index=index+1
            
            
            #Join the threads
            for joiner in range(waitflag):
                    eachthread = threadlist[0]
                    threadlist = threadlist[1:]
                    eachthread.join(1.0)
                    
    
        