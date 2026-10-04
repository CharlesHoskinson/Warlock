import socket,sys,time
s=socket.socket(socket.AF_UNIX);s.bind(sys.argv[1]);s.listen();connections=[]
while True:connections.append(s.accept()[0])
