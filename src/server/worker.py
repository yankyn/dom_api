'''
Created on Nov 28, 2012

@author: Nathaniel
'''
from multiprocessing import Process
import zmq
import json
import dominion

def create_worker(server_addresses, dominion_db = 'DOMINION_SYS'):
    '''
    Start a process for a post worker connecting with zmq to the given addresses.
    Assumes server_addresses in iterable and contains strings.
    '''
    worker = Worker(args=[server_addresses])
    worker.start()
    return worker

class Worker(Process):
    '''
    A worker capable of directly accessing the DB. The two main functionalities for this are posting updates
    to the db and 
    '''

    def __init__(self, *args, **kwargs):
        '''
        We inherit from Process and add 
        '''
        self.kill = False
        return super(Worker, self).__init__(target = self.work, *args, **kwargs)

    def _kill(self):
        '''
        Kills the process.
        '''
        self.kill = True

    def _read(self, socket):
        '''
        Waits for input from the socket, parses it and calls the correct method.
        '''
        while not self.kill:
            request = socket.recv()
            if request == 'kill':
                self.kill()
            else:
                dictionary = json.loads(request) #@UnusedVariable
                pass

    def work(self, server_addresses):
        '''
        This is a zmq subscriber used to recieve requests from the dominion server an either fetch game states
        or post them.
        '''
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        for address in server_addresses:
            print "Starting worker for address %s" % address
            socket.connect(address)
        socket.setsockopt(zmq.SUBSCRIBE, 'kill')
        self._read(socket)