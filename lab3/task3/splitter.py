import pickle
import random
import sys
import time

import zmq

import constTask3

src = constTask3.SRC1
prt1 = constTask3.PORT1
prt2 = constTask3.PORT2
prt3 = constTask3.PORT3

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)

address1 = "tcp://" + src + ":" + prt1
address2 = "tcp://" + src + ":" + prt2
address3 = "tcp://" + src + ":" + prt3

push_socket.bind(address1)
push_socket.bind(address2)
push_socket.bind(address3)

time.sleep(1) # wait to allow all mappers to connect? TODO: idk

for i in range(100):  # generate 100 workloads
    workload = random.randint(1, 100)  # compute workload
    push_socket.send(pickle.dumps((me, workload)))  # send workload to worker
