# -*- mode: python ; coding: utf-8 -*-

import os
import subprocess
import time
import sys



def get_time():
    '''returns local time for use in script'''
    now = time.localtime()
    ascii = time.asctime(now)
    return(ascii)
TIMENOW = get_time()
CHANGELOG = 'changelog.txt'
def write_changelog():
    answer = input("[?] Would like to include changes for this build?: ")
    if (answer.lower() in ["yes", "y"]):
        line = input("[*] please give a brief description of changes: ")
        with open(CHANGELOG, 'a') as changes:
            line = line.strip()
            changes.write("# "+line+"\n")
        return
    elif (answer.lower() in ["no", "n"]):
        print("[*] Not including changes")
        return
    else:
        return
    
block_cipher = None
print("#########################################################################################################")
TIMENOW = get_time()
print(TIMENOW)
print("[*] Starting build process for chat client.....")
print("[*] Setting global values....")
time.sleep(2)
HOME = os.getcwd()

FINALBUILD = HOME+"\\finalbuild"
HOOKSPATH = HOME+'\\finalbuild\\source\\hooks'
SOURCECODE = HOME+'\\finalbuild\\source'
ICONSRCDIR = HOME+'\\finalbuild\\source\\src\\icon'
CLIENTFINAL = HOME+'\\finalbuild\\Client'
SERVERFINAL = HOME+'\\finalbuild\\Server'
SPECFILE = 'ClientChatUI.spec'
BUILDFILE = 'build_instructions.txt'
HOOKFILE = HOME+'\\hooks\\hook-win10toast.py'
CLIENT_EXE = 'ClientChatUI.exe'
CLIENT_CONFIG = 'chat_user.txt'
SERVER_EXE = 'ChatServer.exe'
SERVER_CONFIG = 'config.txt'
CLIENT_FILES = [CLIENT_EXE,CLIENT_CONFIG]
SERVER_FILES = [SERVER_EXE, SERVER_CONFIG]
CLIENTSOURCE = ['ClientChatUI.py', 'resources.py', CLIENT_CONFIG, 'resource.qrc']
ICONSOURCE = ['tray_icon_64.png','tray_icon_128.png', 'window_icon_32.png','chat_server.ico']
SERVERSOURCE = ['ChatServer.py',SERVER_CONFIG]


if os.path.exists(FINALBUILD):
    print("[*] finalbuild path is present.....")
else:
    print("[*] finalbuild path not present creating.....")
    os.makedirs(HOOKSPATH)
    os.makedirs(ICONSRCDIR)
    os.makedirs(CLIENTFINAL)
    os.makedirs(SERVERFINAL)
    

def create_source_zip():
    print("[*] making source.zip.....")
    try:
        if os.path.exists(SOURCECODE):
            os.chdir('finalbuild')
            subprocess.run(['python', '-m','zipfile', '-c', 'source.zip', SOURCECODE])
            os.chdir(HOME)     
    except FileNotFoundError:
        raise

def write_source_code():
    if os.path.isfile('build_instructions.txt'):
        print("[*] Copying build instructions file.....")
        subprocess.call(['cmd', '/C', 'copy', BUILDFILE, SOURCECODE])  
    if os.path.isfile('ClientChatUI.spec'):
        print("[*] Copying spec file.....")
        subprocess.call(['cmd', '/C', 'copy', SPECFILE, SOURCECODE])
    time.sleep(1)
    if os.path.isfile('ClientChatUI.py'):
        print("[*] Copying client source.....")
        for item in CLIENTSOURCE:
            subprocess.call(['cmd', '/C', 'copy', item, SOURCECODE])
    time.sleep(1)
    print("[*] Copying server source.....")
    if os.path.isfile('ChatServer.py'):
        for item in SERVERSOURCE:
            subprocess.call(['cmd', '/C', 'copy', item, SOURCECODE])
    time.sleep(1)
    print("[*] Copying icons.....")
    if os.path.isfile('src\\icon\\chat_server.ico'):
        os.chdir('src\icon')
        for item in ICONSOURCE:
            subprocess.call(['cmd', '/C', 'copy', item, ICONSRCDIR])
    os.chdir(HOME)
    print("[*] Copying hook file.....")
    if os.path.isfile(HOOKFILE):
        os.chdir('hooks')
        subprocess.call(['cmd', '/C', 'copy', HOOKFILE, HOOKSPATH])
    return

print("[*] Done setting globals....")
print("#########################################################################################################")
time.sleep(2)
print("[*] Setting up file data.....")
client_data = [('src\\icon\\*.png', 'src\\icon'),('ClientChatUI.py', '.'),('resources.py','.')]
server_data= [('chatserver.py', '.')]
binary_files = [('src\\icon\\*.ico', 'src\\icon')]
win_dll_path = ['C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLS\\x64']
site_packages = ['C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Python36_64\\Lib\\site-packages']
pyqt5_dll_path = ['C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Python36_64\\Lib\\site-packages\\pyqt5\\qt\\bin\\']

libs_dir = ['C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Python36_64\\libs']

my_hooks = [HOME+'\\hooks']

print("[*] Done with file data.....")
print("#########################################################################################################")
time.sleep(2)
print("[*] Starting ChatClient build......")

client = Analysis(['ClientChatUI.py'],
             pathex=libs_dir+ site_packages+ pyqt5_dll_path+ win_dll_path,
             binaries=binary_files,
             datas=client_data,
             hiddenimports=['PyQt5','win10toast', 'win32com','pathlib','thread','resource', 'multiprocessing', 'org', 'grp','pwd','setuptools','readline'],
             hookspath=my_hooks,
             runtime_hooks=[],
             excludes=['tkinter','PyQt4', 'PySide', 'FixTk','pkg_resources.py2_warn', 'pkg_resources.markers'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
client_pyz = PYZ(client.pure, client.zipped_data,
             cipher=block_cipher)


client_exe = EXE(client_pyz,
             client.scripts,
             client.binaries,
             client.zipfiles,
             client.datas,
             icon = ['src\\icon\\chat_server.ico'],
             name='ClientChatUI',
             debug=False,
             bootloader_ignore_signals=False,
             strip=False,
             upx=True,
             upx_exclude=[],
             runtime_tmpdir='\\',
             console=False )
print("[*] Finished building ChatClient.........")
print("#########################################################################################################")
time.sleep(3)
print("[*] Starting ChatServer build......")
server = Analysis(['ChatServer.py'],
             pathex=[],
             binaries=binary_files,
             datas=server_data,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
server_pyz = PYZ(server.pure, server.zipped_data,
             cipher=block_cipher)
server_exe = EXE(server_pyz,
             server.scripts,
             server.binaries,
             server.zipfiles,
             server.datas,
             icon = ['src\\icon\\chat_server.ico'],
             name='ChatServer',
             debug=False,
             bootloader_ignore_signals=False,
             strip=False,
             upx=True,
             upx_exclude=[],
             runtime_tmpdir=None,
             console=True )
print("[*] Finished building ChatServer.........")
print("#########################################################################################################")
time.sleep(2)
print("[*] switching to dist folder.....")
time.sleep(2)
os.chdir("dist")
if os.path.isfile(CLIENT_EXE):
    print("[*] found the client files continuing.....")
    for file in CLIENT_FILES:
        subprocess.call(['cmd', '/C', 'copy', file, CLIENTFINAL])
time.sleep(2)
if os.path.isfile(SERVER_EXE):
    print("[*] found the server files continuing.....")
    for file in SERVER_FILES:
        subprocess.call(['cmd', '/C', 'copy', file, SERVERFINAL])
os.chdir(HOME)
current= os.getcwd()
TIMENOW = get_time()
print(TIMENOW)
print("[*] Project Build finished.....")
print("###############################################################")
print("[*] Grabbing source files.....")

write_source_code()

print("################################################################")
print("[*] Source files copied.....")
os.chdir(HOME)
create_source_zip()
write_changelog()
