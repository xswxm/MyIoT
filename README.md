# MyIoT

What is myIoT:
1. myIoT is a solution for home automation, it can be implemented on your Raspberry Pi. And it theoretically can enable you to control devices (include other embedded devices connected to the server) and acquire info of these devices. 
2. It is currently based on python (sever part) and Android (Client)
3. It can process HTTPS and Socketio requests.

Theory：
1. Client will first send it username and password to Server
2. The Server will process the message, and then response the Client with a random generated Token if the username and password are correct
3. The Client can use the token to establish a socket connection with the server.
4. Once the Client is disconnected, the Server will remove the token


Major Requirements for server part:
1. flask
2. flask_socketio
3. eventlet
4. OpenSSL

Set up for server part:
1. Generate certifications with OpenSSL
2. Set up nginx for our server
3. Open 'system.cfg' under the root of the server folder, modify devices if necessary. I have put some of my devices in it so you probably have to change the settings
4. Run our server by "python app.py"


Set up for client/app part:
1. Open our certification we generated with any textediter, copy all the content to any online QR Code generator, and download the QR Code provided by the website if necessary
2. Open our App and choose 'Update certification' to scan in our certification
3. Check its settings as the default username is 'uname' and the default password is 'passwd', these settings can be modified in 'system.cfg', and it is also possible for you to change the username and password through our client once it connected to the server
4. Touch 'Sign in' and it will connect to the server if everything is all alright.


Explanation of 'system.cfg':
1. The very first part named 'SYSTEM' is the section for server itself, other sections below is all for devices.
2. For each section of devices, the title of the section is the name displayed on our client/app, and its items usually contains the ports the device used and the type of the device, which you want to display and control on your client/app. That is, if you want the device to be a Switch on your app, then named its 'type' to be Switch


Port forwarding:
1. You can config your router to open certain ports for the server and it can be accessed over the Internet.
2. You can also set up a domain for the serer if you have one


Other things:
1. Change the avatar, etc. as you like
2. Code for the client part will be released later if everyone goes well.
3. Best Wishes!
