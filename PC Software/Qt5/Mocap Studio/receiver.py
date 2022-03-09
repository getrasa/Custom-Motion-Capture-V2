# import time
# import zmq

# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")

# while True:
#     #  Wait for next request from client
#     message = socket.recv()
#     print("Received request: %s" % message)

#     #  Do some 'work'

#     #  Send reply back to client
#     socket.send(b"World")

from multiprocessing.connection import Listener

address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
listener = Listener(address, authkey=b'secret password')
conn = listener.accept()
print('connection accepted from', listener.last_accepted)
while True:
    msg = conn.recv()
    print("Message:", msg)
    # do something with msg
    if msg == 'close':
        conn.close()
        break
listener.close()