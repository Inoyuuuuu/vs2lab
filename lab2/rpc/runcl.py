import rpc
import logging
import threading
import constRPC

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def process_response(response):
    if response == constRPC.OK:
        print("ACK Received")
    else:
        try:
            print("Result: {}".format(response.value))
        except:
            print("Error occured while trying to process the server response.")

def append(data, db_list):
    cl.append(data, db_list, process_response)

base_list = rpc.DBList({'foo'})
data = 'bar'
t_receive = threading.Thread(target=append, args=(data, base_list))
t_receive.start()

print("Doing other stuff while waiting for server answerr.")

#cl.stop()