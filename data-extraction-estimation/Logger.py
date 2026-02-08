import time


class Logger:
    def __init__(self, module):
        self.fileName = "log"
        self.module = module

    def log(self, message):
        file = open(self.fileName, "a")
        t = time.localtime()
        final = f"\n{t[0]}-{t[1]}-{t[2]}:  {t[3]}:{t[4]}:{t[5]} IST\t\tModule: {self.module}\n{message}\n"
        file.write(final)
        file.close()
