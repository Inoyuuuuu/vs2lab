import pickle
import time

import zmq

import constHMR

isRunning = True

with open("./text.txt", "r") as file:
    me = "splitter_0"

    src = constHMR.SRC
    prt = constHMR.PORT1

    context = zmq.Context()
    push_socket = context.socket(zmq.PUSH)

    address = "tcp://" + src + ":" + prt

    push_socket.bind(address)

    time.sleep(10)
    print("waited for clients to connect")

    counter = 0

    for line in file:
        workload = line
        print("{}sending {}".format(counter, workload))
        push_socket.send(pickle.dumps((me, workload)))
        
        time.sleep(0.1)

        counter += 1

        