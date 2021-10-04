
"""Server for multithreaded (asynchronous) chat application."""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import os

def is_windows():  # return windows or fail
    return os.name == "nt"
if is_windows():
    import win32console
#
def get_time():
    '''returns local time for use in script'''
    now = time.localtime()
    ascii = time.asctime(now)
    return(ascii)
#
CHATLOG = "ServerChat_log.txt"
TRACELOG= "ServerTracelog.txt"
UILOG = "ServerUIlog.txt"
TIMENOW = get_time()

def log_event(source, event ,time=False):  # define logging for client to LOGFILE
        '''handles logging of events based on destination. excepts chat,error,console as 
        source, followed by the event. time= var is for time stamping events assumes False
        allows for targeted events. If source is anything else value will go to ui log'''
        if source == 'chat':
            with open(CHATLOG, 'a') as log:
                if time:
                    log.write(event+" "+TIMENOW+"\n")
                else:
                    log.write(event+"\n")
        elif source == 'error':
            with open(TRACELOG, 'a')as err:
                err.write("Exception occurred at "+TIMENOW+" event follows:""\n"+event+"\n")
        elif source == 'console':
            print(event)
        else:
            with open(UILOG, 'a')as gui:
                gui.write(event+"\n")     


def accept_incoming_connections():  # Accepts connections.
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("[*] Connected to server.....", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = '[*] Welcome %s! type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    time.sleep(2)
    msg = "%s has joined the chat!" % name
    print(msg)
    client.send(bytes(msg, "utf-8"))
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        #this try block is for when a client diconnects without using quit cmd
        try:
            msg = client.recv(BUFSIZ)
        except ConnectionResetError as e:
            log_event('error',str(e),False)
            print("%s has left the chat." % name)
            #close the client
            client.close()
            #remove them from our list
            del clients[client]
            #tell everyone they left
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            #exit thread to make availible
            return
        #keep log of chat on screen
        log_event('console', name +': '+str(msg), False)
        # if msg is not quit
        if msg != bytes("{quit}", "utf8"):
            #send it out
            broadcast(msg, name+": ")       
        else:
            #they sent quit
            try:
                #notify server console user has left
                print("%s has left the chat." % name)
                #close the client
                client.close()
                #remove them from our list
                del clients[client]
                #tell everyone they left
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                #exit thread to make availible
                return
               # 
                #probably dont need this it will come out later
            except ConnectionResetError as c:
                log_event('console',"Connection restet exception written to log",True)
                log_event('error',str(c),True)
            except OSError as o:
                log_event('console',"OS Exception written to log",True)
                log_event('error',str(o),True)
            


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)
###############################################################################################
#grabs setup info from file
CONFIGINFOFILE = "config.txt"
CONFIGINFO = []
def get_config_info():  # Grabs user info for chat client
    '''opens 'config.txt' to get ip info for server.Also sets the amount of how many connections to accept. 
    File must be in . of script. Only place keyvalue remove any ' or " from string, order is important
    #
    ex. 192.168.0.1  #ip for server
        5            #how many connections to accept
    '''
    #log_event('chat', "[*] Starting..... ", time=True)
    #log_event('ui', "[*] Looking for chat_user.txt.....",False)
    try:    
        with open(CONFIGINFOFILE, "r") as conftmp:
            #log_event('ui',"[*] Found chat_user.txt.....",False)
            for line in conftmp:
                line = line.strip()
                CONFIGINFO.append(line)
        conftmp.close()
        return(CONFIGINFO[0], CONFIGINFO[1])
            #
    except FileNotFoundError as err:
        print("[*] config.txt was not found please make sure it is present....")
        halt = input("Please press a key to continue...")
        #log_event('error', "[*] chat_user.txt was not found please make sure it is present....",False)
        #sys.exit()


conf = get_config_info()
users = []
clients = {}
addresses = {}

HOST = conf[0]
PORT = 33000
BUFSIZ = 1024

ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    try:
        if is_windows():
            win32console.SetConsoleTitle('Chat Server v1.0')
        SERVER.listen(int(conf[1]))
        log_event('console', "[#] Chat Server.....\n[#] Listening @ " + HOST +':'+ str(PORT)+"\n""[#] Max connections: "+ str(conf[1]))
        log_event('ui',"[*] Chat server has started..."+TIMENOW,False)
        log_event('ui', "[#] Chat Server.....\n[#] Listening @ " + HOST +':'+ str(PORT)+"\n""[#] Max connections: "+ str(conf[1]))
        #print("[#] Chat Server.....\n[#] Waiting for connection....." + HOST +':'+ str(PORT))
        ACCEPT_THREAD = Thread(target=accept_incoming_connections)
        ACCEPT_THREAD.start()
        #ACCEPT_THREAD.join()
        #SERVER.close()
    except KeyboardInterrupt:
        ACCEPT_THREAD.join()
        SERVER.close()
        print("Stopping Server.....")
