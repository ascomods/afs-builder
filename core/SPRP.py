from typing import io
import os, glob
import time, datetime
import core.utils as ut
from .StringTable import StringTable

class SPRP:
    header_size = 64
    header_entry_size = 12

    def __init__(self, name = '', size = 0):
        self.name = name
        self.size = size
        self.entries = []
    
    def get_size(self):
        return self.size

    def read(self, stream: io, start_offset = 0):
        ut.endian = '>'

        self.start_offset = start_offset
        stream.seek(self.start_offset)
        stream.seek(8, os.SEEK_CUR) # skip header + unknown bytes
        entry_count = ut.b2i(stream.read(4))
        stream.seek(4, os.SEEK_CUR) # skip unknown bytes
        
        # Reading header
        name_offset = ut.b2i(stream.read(4))
        if name_offset == 0:
            name_offset += 1
        self.entry_info_size = ut.b2i(stream.read(4))
        string_table_size = ut.b2i(stream.read(4))
        self.data_info_size = ut.b2i(stream.read(4))
        self.data_block_size = ut.b2i(stream.read(4))
        ioram_name_offset = ut.b2i(stream.read(4))
        if ioram_name_offset == 0:
            ioram_name_offset += 1
        self.ioram_data_size = ut.b2i(stream.read(4))
        vram_name_offset = ut.b2i(stream.read(4))
        if vram_name_offset == 0:
            vram_name_offset += 1
        self.vram_data_size = ut.b2i(stream.read(4))
        stream.seek(12, os.SEEK_CUR) # skip unknown bytes
        entry_info_offset = self.start_offset + self.header_size
        string_table_offset = entry_info_offset + self.entry_info_size
        self.string_table = StringTable()
        self.string_table.init(stream, string_table_offset, string_table_size)
        self.name = ut.b2s_name(self.string_table.content[name_offset])
        self.ioram_name = self.string_table.content[ioram_name_offset]
        self.vram_name = self.string_table.content[vram_name_offset]
        
        self.info_offset = string_table_offset + string_table_size
        data_offset = self.info_offset + self.data_info_size

        stream.seek(0)
        self.data = stream.read()

        ut.endian = '<'

    def load(self):
        os.chdir(self.name)
        self.string_table = StringTable()
        name, ext = os.path.splitext(self.name)
        self.string_table.build(name.decode('utf-8'), True)
        
        self.name = name
        self.ioram_name = name + ".ioram".encode("utf-8")
        self.vram_name = name + ".vram".encode("utf-8")

        self.data_info_size = 0
        self.data_block_size = 0
        self.ioram_data_size = 0
        self.vram_data_size = 0
        self.entry_info_size = 0
        
        for elt in glob.glob("*"):
            data_object = SPRPEntry(self.string_table)
            data_object.data_type = elt.encode("utf-8")
            data_object.load()
            self.entries.append(data_object)
            self.data_info_size += data_object.data_entry_size * data_object.data_count
            self.data_block_size += data_object.size
        
        self.entry_info_size = self.header_entry_size * len(self.entries)
        entry_info_offset = self.start_offset + self.header_size
        string_table_offset = entry_info_offset + self.entry_info_size
        self.info_offset = string_table_offset + self.string_table.get_size()
        data_offset = self.info_offset + self.data_info_size

        offset = 0
        for entry in self.entries:
            entry.update_offsets(self.info_offset, data_offset, ut.add_padding(offset))
            size = entry.get_size(True)
            offset += size
            self.size += size
        os.chdir("..")

    def save(self, path):
        path = os.path.join(path, self.name)
        stream = open(path, 'wb')
        stream.write(self.data)
        stream.close()
        date = time.mktime(self.date.timetuple())
        os.utime(path, (date, date))

    def __repr__(self):
        return (
            f'\nclass: {self.__class__.__name__}\n'
            f'name: {self.name}\n'
            f'size: {self.size}\n'
            f'entries: {self.entries}'
        )