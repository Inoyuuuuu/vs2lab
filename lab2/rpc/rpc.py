import constRPC
import threading
import time

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None
        self.threads = []

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        for thread in self.threads:
            thread.join()
        self.chan.leave('client')

    def append(self, data, db_list, process_response):
        assert isinstance(db_list, DBList)

        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server

        msgrcv = self.chan.receive_from(self.server)  # wait for ack response
        
        if msgrcv[1] == constRPC.ACK:
            print("ACK received")
            t_receive = threading.Thread(target=self.receiveFromServer, args=(process_response,))
            self.threads.append(t_receive)
            t_receive.start()

    def receiveFromServer(self, process_response):
        msgrcv = self.chan.receive_from(self.server) # wait for actual response
        process_response(msgrcv[1])


class Server:

    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3
        self.threads = []

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                
                client = msgreq[0] # see who is the caller
                
                self.chan.send_to({client}, constRPC.ACK)

                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    t_append = threading.Thread(target=self.handle_append, args=(client, msgrpc))
                    self.threads.append(t_append)
                    t_append.start()
                else:
                    pass  # unsupported request, simply ignore

    def handle_append(self, client, msgrpc):
        result = self.append(msgrpc[1], msgrpc[2])  # do local call
        time.sleep(10)
        self.chan.send_to({client}, result)  # return response