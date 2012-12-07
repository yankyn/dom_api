'''
Created on Nov 30, 2012

@author: Nathaniel
'''
import pytest
import server
import time
import zmq

TEST_SUB_ADDRESS = "tcp://localhost:1234"
TEST_PUB_ADDRESS = "tcp://*:1234"

@pytest.fixture
def publisher(request):
    '''
    Fixture for creating the publisher, binding it and closing it on finish.
    '''
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(TEST_PUB_ADDRESS)
    '''
    The function used to close the socket on finish
    '''
    def fin():
        socket.close()
    '''
    We add the finalizer so every test closes the socket.
    '''
    request.addfinalizer(fin)
    return socket
    
def test_fixture(publisher):
    '''
    This test is used to make sure that the fixture is working correctly.
    '''
    pass

def test_kill(publisher):
    print 'testing kill message'
    print 'creating worker'
    worker = server.create_worker([TEST_SUB_ADDRESS])
    time.sleep(1)
    print 'sending kill'
    publisher.send('kill')
    time.sleep(1)
    
    try:
        assert not worker.is_alive()
    except Exception:
        worker.terminate()
        raise 
    
