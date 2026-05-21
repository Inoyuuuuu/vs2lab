import pickle
import sys
import time
import os

import zmq

import constHMR

me = "reducer_0"
try:
    me = "reducer_{}".format(str(sys.argv[1]))
except NameError:
    print(NameError)

src = constHMR.SRC
reducer1_prt = constHMR.PORT2
reducer2_prt = constHMR.PORT3
reducer1_address = "tcp://" + src + ":" + reducer1_prt
reducer2_address = "tcp://" + src + ":" + reducer2_prt

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)

if me == "reducer_0":
    pull_socket.bind(reducer1_address) 
else:
    pull_socket.bind(reducer2_address) 

time.sleep(5) 

print("{} started".format(me))

wordsDict = {}

while True:
    work = pickle.loads(pull_socket.recv())
    word = work[1]
    word = word.strip("\n")

    if word == "":
        continue

    if wordsDict.get(word) != None:
        wordsDict[word] += 1
    else:
        wordsDict[word] = 1
    
    wordsDict = dict(sorted(wordsDict.items(), key=lambda item: item[1], reverse=True))
    
    os.system('cls' if os.name == 'nt' else 'clear')

    output = ""
    for key, values in wordsDict.items():
        wordOut = "\"{}\": {} | ".format(key, values)
        output += wordOut
    print(output)
    
    
