try:
    #py3 ver first
    import _thread as thread
except ImportError:
    #py2 ver instead
    import thread
import time
import sys
import webbrowser
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit, QMainWindow, QApplication, QStyle, QWidget, QPushButton, QAction, QTextEdit, QFrame, QVBoxLayout, QScrollArea, QMessageBox, QStatusBar, QFileDialog, QInputDialog, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QKeyEvent, QTextCursor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRect, QUrl, Qt, QObject
from socket import AF_INET, socket, SOCK_STREAM
import subprocess
import os
import win10toast
from pathlib import PureWindowsPath
#import our resource file with icons and such
import resources

def is_windows():  # return windows or fail
    return os.name == "nt"
#

if is_windows():
    
   

    def get_time():
        '''returns local time for use in script'''
        now = time.localtime()
        ascii = time.asctime(now)
        return(ascii)
    WELCOME = 0
    TRACELOG = "Error_log.txt"
    CHATLOG = "chatclient_log.txt"
    UILOG = "ui_log.txt"
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
    #####################################################################################
    USERINFOFILE = "chat_user.txt"
    USERINFO = []
    def get_user_info():  # Grabs user info for chat client
        '''opens 'chat_user.txt' to get auth info for chat client.File must be in . of script.
        Only place keyvalue remove any ' or " from string, order is important
        ex. 192.168.0.1  #host to connect to
            username     #Username for chat client
            25575        #port to connect to
        '''
        log_event('chat', "[*] Starting..... ", time=True)
        log_event('ui', "[*] Looking for chat_user.txt.....",False)
        try:    
            with open(USERINFOFILE, "r") as usrtemp:
                log_event('ui',"[*] Found chat_user.txt.....",False)
                for line in usrtemp:
                    line = line.strip()
                    USERINFO.append(line)
            usrtemp.close()
            return(USERINFO[0], USERINFO[1])
            #
        except FileNotFoundError as err:
            print("[*] chat_user.txt was not found please make sure it is present....")
            log_event('error', "[*] chat_user.txt was not found please make sure it is present....",False)
            sys.exit()
    #####################################################################################
    class ToastMessages(win10toast.ToastNotifier): # Custom class for enabling toast notifications
        '''Inherits from main Class to add functions.Enables toast\balloon tips on windows 7/8/10 , 08/12/16'''
        def __init__(self):
            super().__init__()
            pass
        #
        def grab_event_info(self):
            #print('hey')
            pass

        def on_event(self):
            self.grab_event_info()
            
        #
        def get_icon_path(self):
            '''override default icon with custom one. we pass this to showtoast as a path object'''
            #setup blank icon
            new_icon = ''
            #change to icon dir
            os.chdir("src\icon")
            #set home path for directory
            homedir = os.getcwd()
            icon = 'tray_icon_128.png'
            #icon = QIcon(':/src/icon/tray_icon_128.png')
            #icon = 'toast_events_icon.ico'
            #create path object to pass
            icondir = PureWindowsPath(homedir,icon)
            if os.path.isfile(icon):
                new_icon = icondir
            else:
                #else fall back and use default of class
                new_icon = None
            print(new_icon)
            return new_icon
    #####################################################################################
    class Stream(QObject):  # Custom class for handling stdout
        '''class for handling stdout from print statements on imported code '''
        newText = pyqtSignal(str)

        def write(self, text):
            self.newText.emit(str(text))

        def readline(self):
            #self.newText.readline()
            pass
            
        def flush(self):
            pass
    #####################################################################################
    class Chatclient():  # Custom Chatclient class
        '''Handles creating chat client given a ip and optional port.
        ex. client = ChatClient(ip,port)'''
        def __init__(self, address , port):
            try:
                self.user = USERINFO[1]
                self.HOST = address
                self.PORT = port
                self.BUFSIZ = 1024
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                if not self.PORT:
                    self.PORT = 33000
                else:
                    self.PORT = int(port)
            except Exception as e:
                print(e)
                #

        def receive(self):
            """Handles receiving of messages."""
            start_toast = ToastMessages()
            
            while True:
                try:
                    msg = self.client_socket.recv(self.BUFSIZ).decode("utf8")
                    log_event('console', str(msg),False)
                    log_event('chat', str(msg),False)
                    if msg == '{quit}':
                        log_event('console', "recieved quit ok from server")
                    #build in logic to prevent certain msgs from being dislayed?
                    noprint = msg.find(self.user)
                    if noprint == -1:
                        start_toast.show_toast("Chat Client",
                        msg,
                        icon_path= None,
                        duration=1,
                        threaded=True,
                        callback_on_click=start_toast.on_event()
                        )
                    else:
                        pass
                except OSError as e:
                    log_event('error', "[!] The server might be down or you quit your session.....",False)
                    log_event('console',"[!] The server might be down or you quit your session.\n[*] check the logs for more info",False)
                    log_event('error', "[!] An exception occured in receive function of chatclient. The error is " + str(e)+ "\n"+"[?] If you quit your session you can safely ignore this issue",True)
                    return
        
        def send_msg(self, msg):
            """Handles sending of messages."""
                #user = USERINFO()
            response = []
            try:
                if msg == "{quit}":
                    log_event('chat', "[!] quit cmd was sent \n[!] Disconnecting from server.....",False)
                    self.client_socket.send(bytes(msg, "utf8"))
                    self.client_socket.close()
                else:
                    self.client_socket.send(bytes(msg, "utf8"))
            except Exception as e:
                log_event('chat',"[!] Unable to send msg to server.....",False)
                log_event('error', "[*] An exception occured in send_msg function of chatclient. The error is " + str(e),False)
                log_event('console',"[!] Unable to send msg to server.....",False)
                return

        def connect_server(self, uid, srv):
            '''connects to up stream server'''
            try:
                ADDR = (srv, self.PORT)
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.client_socket.connect(ADDR)
            except ConnectionRefusedError as e:
                log_event('console', "[!] Unable to connect.....")
                log_event('chat', "[!] Unable to connect.....")
                log_event('error', "[!] An exception occured in connect_server function of chatclient. The error is " + str(e)+"\n"+"[?] Possible reasons could be wrong ip address or server is not currently up.",False)
                return e
        #
        def stop_client(self):
            self.send_msg('{quit}')      
    #####################################################################################
    class App(QMainWindow):  # Main app window
        def __init__(self):
            super().__init__()
            self.title = 'Chat Cilent'
            self.width = 320
            self.height = 400
            #self.prompt = "[*] \\: "
            self.word_list = []
            self.cmd_input = []
            self.chat_msg = []
            self.usrinfo = get_user_info()
            self.chatserver = self.usrinfo[0]
            self.chatuser = self.usrinfo[1]
            self.chatlog = CHATLOG
            self.errlog = TRACELOG
            self.initUI()
            #capture all std output with our class
            sys.stdout = Stream(newText=self.onUpdateText)
            sys.stderr = Stream(newText=self.onUpdateText)
            sys.stdin = Stream(newText=self.onUpdateText)
        #

        def onUpdateText(self, text):
            cursor = self.txt.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            self.txt.setTextCursor(cursor)
            self.txt.ensureCursorVisible()
        #
        def __del__(self):
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            sys.stdin = sys.__stdin__
        #
        def activate_on_click(self, reason):
            '''when user single left-click  tray icon
            this will show/hide main artillery window'''
            if reason == QSystemTrayIcon.Trigger:
                if self.isVisible():
                    self.hide()
                else:
                    self.show()
        #
        def quit(self):
            pass
        #
        def initUI(self):
            '''This method creates our GUI'''
            #######################################################
            #create the main layout first
            log_event('ui', "[*] Loading UI.....",False)
            self.centralwidget = QWidget()  
            lay = QVBoxLayout()
            self.setFixedSize(self.width, self.height)
            self.setWindowTitle(self.title)
            self.setCentralWidget(self.centralwidget)
            
            ########################################################
            #create individual menu names for use
            mainMenu = self.menuBar()
            #connectMenu = mainMenu.addMenu('Connect')
            settingsMenu = mainMenu.addMenu('Settings')
            logMenu = mainMenu.addMenu('Logs')
            helpMenu = mainMenu.addMenu('Help')
            ########################################################
            #buttons for connect menu.
            #newButton = QAction('default...', self)
            #newButton.triggered.connect(self.chat_client_thread)
            #newButton.triggered.connect(self.run_artillery)
            #
            #existingbutton = QAction('Existing...', self)
            #existingbutton.triggered.connect(self.kill_artillery)
            #existingbutton.triggered.connect(self.close)
            #
            #exitButton = QAction('Exit...', self)
            #exitButton.setShortcut('Ctrl+Q')
            #exitButton.triggered.connect(self.close)
            #
            #connectMenu.addAction(newButton)
            #connectMenu.addAction(existingbutton)
            #connectMenu.addAction(exitButton)
            ########################################################
            #buttons for settings menu
            viewSettings = QAction('View Current', self)
            viewSettings.triggered.connect(self.get_settings)
            #
            changeSettings = QAction('Modify', self)
            changeSettings.triggered.connect(self.get_settings_txt)
            #
            importSettings = QAction('Import...',self)
            importSettings.triggered.connect(self.import_settings)
            #
            exportSettings = QAction('Export...',self)
            exportSettings.triggered.connect(self.export_settings)
            #
            settingsMenu.addAction(viewSettings)
            settingsMenu.addAction(changeSettings)
            settingsMenu.addAction(importSettings)
            settingsMenu.addAction(exportSettings)
            #########################################################
            #buttons for Logmenu
            viewLogs = QAction('Chat Logs...',self)
            viewLogs.triggered.connect(self.chat_log_thread)
            #
            saveLogs = QAction('Error Logs...', self)
            saveLogs.triggered.connect(self.error_logs)
            #
            #clearLogs = QAction('Clear...', self)
            #clearLogs.triggered.connect(self.flush_logs)
            #
            logMenu.addAction(viewLogs)
            logMenu.addAction(saveLogs)
            #logMenu.addAction(clearLogs)
            #########################################################
            #buttons for Helpmenu
            getAbout = QAction('About', self)
            getAbout.triggered.connect(self.get_about)
            #
            getWebsite = QAction('Homepage',self)
            getWebsite.triggered.connect(self.get_about_website)
            #
            getHelp = QAction('Help...',self)
            getHelp.triggered.connect(self.get_help)
            #
            helpMenu.addAction(getAbout)
            helpMenu.addAction(getWebsite)
            helpMenu.addAction(getHelp)
            #############################################################
            #create main area to grab output from app
            self.txt = QTextEdit(self.centralwidget)
            self.txt.setObjectName("output_frame")
            self.txt.setFrameShadow(QFrame.Raised)
            self.txt.setLineWrapMode(QTextEdit.WidgetWidth)
            self.txt.setReadOnly(True)
            self.txt.setFontFamily('Comic-sans')
            self.txt.setFontPointSize(10)
            self.txt.setFixedHeight(300)
            self.txt.setFixedWidth(self.width)
            ##############################################################
            #setup chat client for use
            self.chat = Chatclient(self.chatserver , False)
            ##############################################################
            #create line edit for window and msg button
            self.chat_linedit = QLineEdit(self.centralwidget)
            self.chat_linedit.keyPressEvent = self.keyPressEvent
            self.chat_linedit.setGeometry(QRect(60, 325, 201, 20))
            ##############################################################
            #build and show final window
            self.start_message = "[*] Type connect to start chat.\n"
            self.txt.append(self.start_message)
            lay.addWidget(self.chat_linedit)
            lay.addWidget(self.txt)
            log_event('ui', "[*] Done loading UI.....",False)
            self.show()
            #########################################################
        #
        def connect_chat(self):
            '''open txt input box for ip info on server to connect to
             and returns a tuple of info for chat_client_thread()'''
            
            address, ok = QInputDialog.getText(self, 'Connect to server',
                'Please enter ip:')
            if ok:
                #id = 'russ'
                ip = address
            user, ok = QInputDialog.getText(self, 'Choose Username',
                'Please enter name:')
            if ok:
                id = user
            #return id,ip
            #thread.start_new_thread(self.connect_to_server,(id,ip))
        #
        def chat_client_thread(self):
            try:
                log_event('chat',"[*] Trying to connect to server.....")
                log_event('console', "[*] Trying to connect to server.....")
                try:
                    self.chat.connect_server(self.chatuser,self.chatserver)
                    log_event('chat', "[*] Connected.....",False)
                    thread.start_new_thread(self.chat.receive,())
                    log_event('chat', "[*] Recieve thread started.....\n[*] Sending user info.....",False)
                    self.chat.send_msg(self.chatuser)
                except ConnectionRefusedError as e:
                    print(str(e))
                
            except Exception as e:
                log_event('error',"[*] An exception occured in chat_client_thread function of InitUI. The error is " + str(e),False)
        #
        def openFileNameDialog(self):
            '''creates open file dialog box'''
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,"Import file.....", "","All Files (*);;Python Files (*.py)", options=options)
            if fileName:
                print(fileName)
        #
        def saveFileDialog(self):
            '''creates save file  dialog box'''
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self,"Save as......", "","All Files (*);;Text Files (*.txt);;Log Files (*.log)", options=options)
            if fileName:
                print(fileName)
        #
        def get_settings(self):
            pass
        #
        def get_settings_txt(self):
            pass
        #
        def import_settings(self):
            pass
        #
        def export_settings(self):
            pass
        #
        def flush_logs(self):
            '''overwrites logfile with nothing after asking if you want to save a copy first.'''
            pass
        #
        def error_logs(self):
            '''opens error logs with default txt veiwer'''
            try:
                subprocess.run(['notepad', self.errlog],shell=False)
            except Exception as err:
                print(err)
        #
        def chat_logs(self):
            '''opens chat logs with default txt veiwer'''
            try:
                subprocess.run(['notepad', self.chatlog],shell=False)
            except Exception as err:
                print(err)
        #
        def chat_log_thread(self):
            thread.start_new_thread(self.chat_logs,())
        #
        def get_help(self):
            '''presents msgbox with chosen message'''
            try:
                msg = QMessageBox()
                msg.setWindowTitle("Help")
                msg.setText("The below cmds are supported:")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setInformativeText('connect - connects to upstrem server\nhelp - this menu\nexit - closes this window')
                help = msg.exec_()
            except Exception as err:
                print(err)
        #
        def get_about(self):
            '''opens an about dailog with info about program'''
            try:
                msg = QMessageBox()
                msg.setWindowTitle("Chat Client v1.0")
                msg.setText("[*] Interface created with Pyqt5.\n[*] Python ver. 3.6.6\n[*] Executable built with pyinstaller 4.0")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setInformativeText('')
                help = msg.exec_()
            except Exception as err:
                print(err)
        #
        def get_about_website(self):
            '''opens main github page with google_chrome browser'''
            try:
                open_google = webbrowser.get('windows-default').open('https://github.com/russhaun/Chat')
            except Exception as err:
                print(err)
        #
        def keyPressEvent(self, e):
            '''grabs keys to be used for internal commands and returns command'''
            if type(e) == QtGui.QKeyEvent:
                code = QKeyEvent.key(e)
                backspace = 16777219
                backspace_txt = str(backspace)
                #enter_key_press = 16777220
                self.code_txt =str(code)
                self.answer = e.text()
                try:
                    #add every key typed to screen until enter recieved
                    self.chat_linedit.insert(self.answer)
                    #add key to list for next step
                    self.word_list.append(self.answer)
                    # if backspace hit clears entry
                    if self.code_txt == backspace_txt:
                        self.chat_linedit.clear()
                        self.word_list.clear()
                    #once enter is hit. read word and execute command
                    if self.answer == '\r':
                        self.chat_linedit.clear()
                        self.word_list.remove('\r')
                        s = "".join(self.word_list)
                        self.cmd_input.append(s)
                        self.word_list.clear()
                        self.command = self.cmd_input[0]
                        #
                        if self.command == "connect":
                            self.cmd_input.clear()
                            self.chat_client_thread()
                        elif self.command == 'exit':
                            self.cmd_input.clear()
                            self.chat.stop_client()
                            log_event('chat', "[!] Chatclient was stopped.....",False)
                            #allows logs to be written out properly
                            time.sleep(3)
                            self.close()
                        elif self.command == 'help':
                            self.cmd_input.clear()
                            self.get_help()
                        elif self.command == 'imports':
                            #print(dir(globals))
                            #self.imports()
                            pass
                        else:
                            self.chat.send_msg(self.command)
                            self.cmd_input.clear()
                except Exception as err:
                    print(err)
        #
#########################################################################################
if __name__ == '__main__': #sets up main app and creates tray app in the system tray
    app = QApplication([])
    app.setStyle('Fusion')
    #load icons from our resource file
    app.setWindowIcon(QIcon(':/src/icon/window_icon_32.png'))
    tray_icon =QIcon(':/src/icon/tray_icon_128.png')
    ex = App()
    #create system tray object
    tray = QSystemTrayIcon()
    tray.setIcon(tray_icon)
    tray.setToolTip("Chat Client v1.0")
    tray.setVisible(True)
    #create right-click context menu for tray object
    contextmenu = QMenu()
    startmenu = QAction("Start.....")
    startmenu.triggered.connect(ex.chat_client_thread)
    contextmenu.addAction(startmenu)
    settingsmenu = QAction("Settings.....")
    settingsmenu.triggered.connect(ex.get_settings)
    contextmenu.addAction(settingsmenu)
    exitmenu = QAction("Exit...")
    exitmenu.triggered.connect(app.quit)
    contextmenu.addAction(exitmenu)
    tray.setContextMenu(contextmenu)
    #setup single click on icon to show/hide window
    tray.activated.connect(ex.activate_on_click)
    sys.exit(app.exec_()) 
