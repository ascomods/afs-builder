import os
import core.utils as ut

class AFL:
    entry_name_size = 32

    def __init__(self):
        self.entries = []
    
    def add(self, entry_name):
        self.entries. \
            append((entry_name[:32]) if len(entry_name) > 32 else entry_name)
    
    def read(self, stream):
        stream.seek(12, os.SEEK_CUR)
        entry_count = ut.b2i(stream.read(4))

        start_entry_offset = stream.tell()
        for i in range(entry_count):
            self.entries.append(ut.read_until(stream, start_entry_offset + i * self.entry_name_size))

    def write(self, stream):
        stream.write(ut.s2b_name(self.__class__.__name__) + b'\0')
        stream.write(b'\x01\x00\x00\x00')
        stream.write(b'\xFF\xFF\xFF\xFF')
        stream.write(ut.i2b(len(self.entries)))

        for entry in self.entries:
            stream.write(entry.ljust(32, b'\0'))
    
    def __repr__(self):
        return (
            f'\nclass: {self.__class__.__name__}\n'
            f'\nentry count: {len(self.entries)}\n'
            f'\nentries: {self.entries}\n'
        )