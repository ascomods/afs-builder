from typing import io
import os, glob
import time, datetime
import core.utils as ut

class STPK:
    start_offset = 16

    def read(self, stream: io):
        # Read only first entry info
        stream.seek(self.start_offset + 16)
        data_name = ut.read_string(stream, 32, 32).strip(b'\x00')
        self.name = ut.b2s_name(data_name)

        stream.seek(0)
        self.data = stream.read()
    
    def save(self, path):
        stream = open(os.path.join(path, self.name), 'wb')
        stream.write(self.data)
        stream.close()
        date = time.mktime(datetime.datetime.today().timetuple())
        os.utime(path, (date, date))