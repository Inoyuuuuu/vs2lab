import rpc
import logging
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def process_response(response):
    try:
        print("Result: {}".format(response.value))
    except:
        print("Error occured while trying to process the server response.")    

base_list = rpc.DBList({'foo'})
data = 'bar'

cl.append(data, base_list, process_response)

print("Doing other stuff while waiting for server answer.")
time.sleep(3)
print("Doing stuff...")
time.sleep(3)
print("Still doing stuff...")
time.sleep(3)
print("STILL DOING STUFF...")
time.sleep(3)

cl.stop()