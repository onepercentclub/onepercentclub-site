import time


# Source:
# http://preshing.com/20110924/timing-your-code-using-pythons-with-statement

class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start