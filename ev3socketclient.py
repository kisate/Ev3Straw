import socket, threading

class Client():

    def __init__(self, host, port):

        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def reader(self, s):
        while self.on:    
            message = []

            part = s.recv(1)
            
            message_size = int.from_bytes(part, byteorder='big')

            for i in range(message_size):
                part = s.recv(8)
                message.append(int.from_bytes(part, byteorder='big', signed=True))

            #print (message)
            
            self.messageHandler.updateMessage(message)
            
            if len(part) == 0 : break


    def connect(self, messageHandler):
        self.socket.connect((self.host, self.port))
        self.on = True

        self.messageHandler = messageHandler
        threading.Thread(target=self.reader, args=(self.socket,)).start()

    def send(self, *args):
        
        msg = len(args).to_bytes(1, byteorder='big')

        for a in args:
            msg += (a).to_bytes(8, byteorder='big', signed = True)

        self.socket.send(msg)

    def disconnect(self):
        self.on = False
        self.socket.close()
