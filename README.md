Chat client/server v1.0

chat server and client written with pyqt5 and python 3.
compiled to an exe with pyinstaller 4

### Client features:

1. allows multiple clients good for small networks

2. tray app to allow hiding of main window(runs in background)

3. full logging of chat(optional) and software.

4. basic help menu

### Server features:

1. it sends and receives messages to/from clients on network using TCP

2. not much more to say

### Planned client features:

1. Windows Toast Notifications

2. allow run as a service

3. allow sending images/files

4. any suggested features

### Supported platforms

- Windows 10 21H1  Build 19043

- note:
        might run on other OSe's have no clue.
        please lmk if it does or doesn't. will add more as it progresses

### Bugs and enhancements

For bug reports or enhancements, please open an issue here https://github.com/russhaun/Chat/issues


###  Usage:


### Server
- on the machine you decide to host the server on copy server exe and config.txt to place of your choosing, edit config.txt with the ip of server and how many clients u wish to accept. then double-click exe server will start listening for connections. when done properly you should receive this:

![chat_server_sucess](https://user-images.githubusercontent.com/20805369/129812703-4b32fe8e-a55d-4e35-bb0d-a58eb89a7608.png)




### Client

- copy client to place of your choosing edit chat_user.txt with ip of server and username of your choice. when client opens type connect to start session. Typing exit will close session and exit app.

on opening the client just type connect in the space provided

![chatclientconnect](https://user-images.githubusercontent.com/20805369/129812746-9ad3a516-d88d-4f70-9c1d-b2eefebf474b.png)


on sucess you should see this:

![chatconnectsucess](https://user-images.githubusercontent.com/20805369/129812845-8aa8d200-24ab-4c3c-94e7-afff1641cdfe.png)


if for some reason the server is down or ip incorrect you should receive:

![chatconnectfailure](https://user-images.githubusercontent.com/20805369/129812947-f8ae4474-c132-41de-9446-d095b6c9e1a4.png)


