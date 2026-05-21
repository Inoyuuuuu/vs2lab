import pickle
import sys
import time

import zmq

import constHMR

me = "mapper_0"
try:
    me = "mapper_{}".format(str(sys.argv[1]))
except NameError:
    print(NameError)

src = constHMR.SRC
splitter_prt = constHMR.PORT1
reducer1_prt = constHMR.PORT2
reducer2_prt = constHMR.PORT3

splitter_address = "tcp://" + src + ":" + splitter_prt
reducer1_address = "tcp://" + src + ":" + reducer1_prt
reducer2_address = "tcp://" + src + ":" + reducer2_prt

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)
pull_socket.connect(splitter_address) 

push_socket_R1 = context.socket(zmq.PUSH)
push_socket_R1.connect(reducer1_address) 

push_socket_R2 = context.socket(zmq.PUSH)
push_socket_R2.connect(reducer2_address) 

time.sleep(1) 

print("{} started".format(me))

while True:
    work = pickle.loads(pull_socket.recv())
    print("{} received {} from {}".format(me, work[1], work[0]))

    words = work[1].split(" ")

    for word in words:
        if ord(word[0].lower()) % 2 == 0:
            push_socket_R1.send(pickle.dumps((me, word)))
        else:
            push_socket_R2.send(pickle.dumps((me, word)))
    
