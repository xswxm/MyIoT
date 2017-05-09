# MyIoT

What is myIoT:
1. myIoT is a solution for home automation, it can be implemented on your Raspberry Pi. It theoretically can enable you to control devices (include other embedded devices connected to the server) and acquire info of these devices. 
2. It is currently based on python (sever part) and Android (Client)
3. It can process HTTPS and socket.io requests.

Theory：
1. Client will first send it username and password to Server
2. The Server will process the message, and then response the Client with a random generated Token if the username and password are correct
3. The Client can use the token to establish a socket.io connection with the server.
4. Once the Client is disconnected, the Server will remove the token


Dependencies - server:
1. flask
2. flask_socketio
3. eventlet
4. OpenSSL
5. pigpio

Dependencies - client:
1. zxing: https://github.com/zxing/zxing
2. SwipeDelMenuLayout: https://github.com/mcxtzhang/SwipeDelMenuLayout

Set up for server part:
1. Generate certifications with OpenSSL
2. Set up nginx for our server
3. Run our server by "python app.py"


Set up for client/app part:
1. Open our certification we generated with any textediter, copy all the content to any online QR Code generator, and download the QR Code provided by the website if necessary
2. Open our App and choose 'Update certification' to scan in our certification
3. Check its settings as the default username is 'uname' and the default password is 'passwd', these settings can be modified in 'system.cfg', and it is also possible for you to change the username and password through our client once it connected to the server
4. Touch 'Sign in' and it will connect to the server if everything is all alright.
5. Add your device from the Client App


Explanation of 'system.cfg':
1. The very first part named 'DEFUALT' is the section for server itself.

Explanation of the 'device.py'
1. You have to modify this file as the devices/sensors I have are not the same as yours, so remove them as necessary

Explanation of the 'add.py'
1. You can manually add devices though this script rather from the Client App
2. Do modify this file before adding your devices

Port forwarding:
1. You can config your router to open certain ports for the server and it can be accessed over the Internet.
2. You can also set up a domain for the serer if you have one


Other things:
1. Change the avatar, etc. as you like
2. Best Wishes!
