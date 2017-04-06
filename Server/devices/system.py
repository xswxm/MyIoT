import threading, os

class CPUTemp:
    _lock = threading.RLock()
    def __init__(self, title, id = 1000):
        self.id = id
        self.title = title
        self.type = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        try:
            with CPUTemp._lock:
                res = os.popen('vcgencmd measure_temp').readline()
            return res.replace("temp=","").replace("'C\n","") + " 'C"
        except Exception as e:
            return str(e)
