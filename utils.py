import threading
import copy
HEADER = 64

# MESSAGE PROTOCOL:
# 1st message to server must contain client type
# Messages have two parts:
#   first: sending the length of the message so
#   the server knows how much mem to allocate
#   second: the actual message contents
def send_message(client, header_msg, msg):
        padded_header_msg = header_msg + b' ' * (HEADER - len(header_msg))
        client.send(padded_header_msg)
        client.send(msg)

# haven't tested on non numpy objects
class LockedObject(object):
    """
    Thread safe object
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.val = None

    def __get__(self, obj, objtype):
        self.lock.acquire()
        if self.val != None:
            # return a copy of the data could be slowing us down but safer
            if isinstance(ret_val, np.ndarray):
                ret_val = self.val.copy()
            else:
                ret_val = copy.deep_copy(self.val)
        else:
            ret_val = None
        self.lock.release()
        # print('getting', ret_val)
        return ret_val

    def __set__(self, obj, val):
        self.lock.acquire()
        # print('setting', val
        # speed up for nparrays
        if isinstance(val, np.ndarray):
            self.val = val.copy()
        else:
            self.val = copy.deep_copy(val)
        self.lock.release()
