import threading
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
            ret_val = self.val.copy()
        else:
            ret_val = None
        self.lock.release()
        # print('getting', ret_val)
        return ret_val

    def __set__(self, obj, val):
        self.lock.acquire()
        # print('setting', val
        self.val = val.copy()
        self.lock.release()