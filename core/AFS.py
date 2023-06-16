from io import BytesIO
from typing import io
import os, glob
import time, datetime
import struct
import re
import core.utils as ut
import core.common as cm
from core.AFL import AFL
from core.STPZ import STPZ, OLCS, ODCS, SCDO, SCLO
from core.STPK import STPK
from core.SPRP import SPRP
from core.SPR3 import SPR3

class AFS:
    def __init__(self, name = ''):
        self.name = name
        self.entries = []
        self.size = 0

    def update_offsets(self):
        self.info_offset = 8
        data_offset = self.info_offset + (1 + len(self.entries) * 8)
        self.data_offset = ut.add_padding(data_offset, 2048)
        self.size = 0
        for entry in self.entries:
            entry.offset = self.data_offset + self.size
            self.size += ut.add_padding(entry.size, 2048)

    def get_size(self):
        size = 0
        for entry in self.entries:
            size += entry.size
        return size
    
    @ut.keep_cursor_pos
    def get_entry_info_offset(self, stream):
        stream.seek(8 * self.file_count, os.SEEK_CUR)
        self.entry_info_offset = ut.b2i(stream.read(4))

    def read(self, stream):
        # Reading data info after data tag
        stream.seek(4)
        self.file_count = ut.b2i(stream.read(4))
        self.get_entry_info_offset(stream)

        for i in range(self.file_count):
            entry = AFSEntry(str(i), self.entry_info_offset + (48 * i))
            entry.offset = ut.b2i(stream.read(4))
            entry.size = ut.b2i(stream.read(4))
            entry.read(stream)
            if entry.name == '':
                entry.name = f"unnamed_{i}"
            self.entries.append(entry)

    def compress(self):
        for entry in self.entries:
            entry.compress()

    def decompress(self):
        for i in range(len(self.entries)):
            self.entries[i].decompress()

    def write(self, stream):
        # Writing entry offset + size
        stream.write(ut.s2b_name(self.__class__.__name__) + b'\x00')
        stream.write(ut.i2b(len(self.entries)))

        
        for entry in self.entries:
            try:
                stream.write(ut.i2b(entry.offset))
                stream.write(ut.i2b(entry.size))
            except Exception as e:
                print(e)
        # For details list
        self.entry_info_offset = stream.tell()
        self.write_data(stream)
    
    def write_data(self, stream):
        for entry in self.entries:
            entry.write(stream)

        # For details list
        entry_info_offset = ut.add_padding(stream.tell(), 2048)
        stream.seek(self.entry_info_offset)
        self.entry_info_offset = entry_info_offset
        stream.write(ut.i2b(self.entry_info_offset))
        stream.write(ut.i2b(len(self.entries) * 48))
        stream.seek(self.entry_info_offset)

        for entry in self.entries:
            entry.write_details(stream)

    def load(self, path):
        is_dir = False
        if os.path.isdir(path):
            os.chdir(path)
            is_dir = True
        
        for elt in glob.glob('*'):
            entry = AFSEntry(elt)
            entry.load()
            self.entries.append(entry)
            self.size += entry.size
        
        self.entries.sort(key=lambda e: ut.natural_keys(e.name))

        # removing prefix
        for entry in self.entries:
            entry.name = re.sub('^\[\d+\]', '', entry.name)

        self.update_offsets()

        if is_dir:
            os.chdir('..')

    def save(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

        for i in range(len(self.entries)):
            if not re.match(r'^\[\d+\]', self.entries[i].name):
                self.entries[i].name = f'[{i}]{self.entries[i].name}'
            self.entries[i].save(path)
    
    def save_AFL(self, stream):
        afl_object = AFL()
        for entry in self.entries:
            afl_object.add(ut.s2b_name(entry.name))
        afl_object.write(stream)

    def __repr__(self):
        return (
            f'\nclass: {self.__class__.__name__}\n'
            f'\nentry count: {len(self.entries)}\n'
            f'\ntotal size: {self.get_size()}\n'
            f'\nentries: {self.entries}\n'
        )

class AFSEntry:
    def __init__(self, name = '', entry_info_offset = 0):
        self.name = name
        self.entry_info_offset = entry_info_offset

    @ut.keep_cursor_pos
    def read(self, stream):
        stream.seek(self.offset)
        self.data = stream.read(self.size)
        stream.seek(self.entry_info_offset)
        self.name = ut.b2s_name(stream.read(32).replace(b'\0', b''))
        date = struct.unpack('hhhhhh', stream.read(12))
        self.date = datetime.datetime(*date)

    def compress(self):
        try:
            data_tag = self.data[:4]
            data_tag = ut.b2s_name(data_tag).replace('0', 'O')
            stpz_object = STPZ()
            stpz_object.data = self.data
            stpz_object.compress()
            self.data = stpz_object
        except Exception as e:
            odcs_object = ODCS()
            odcs_object.data = self.data
            odcs_object.compress()
            self.data = odcs_object

    def decompress(self):
        data_tag = self.data[:4]
        try:
            data_tag = ut.b2s_name(data_tag).replace('0', 'O')
            data_object = eval(data_tag)()
            data_object.read(BytesIO(self.data[4:]))
            self.data = data_object.decompress(True)

            if hasattr(data_object, 'data'):
                self.data = data_object.data
            data_class_name = self.data.__class__.__name__
            name, ext = os.path.splitext(self.name)

            if data_class_name != 'bytearray':
                self.data.date = self.date
                if (data_class_name in cm.ext_map):
                    ext = cm.ext_map[data_class_name][0]
                    if (name.endswith("_s") and ("SPR" in data_class_name)):
                        name = name[:-2]
                    self.name = f"{name}{ext}"
            else:
                if (name.endswith("_v")):
                    name = name[:-2] + ".vram"
                elif (name.endswith("_i")):
                    name = name[:-2] + ".ioram"
                self.name = name
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()

    def write(self, stream):
        stream.seek(self.offset)
        if self.data.__class__.__name__ != 'bytes':
            self.data.write(stream)
        else:
            stream.write(self.data)

    def write_details(self, stream):
        name = ut.extb(ut.s2b_name(self.name[:31]), 32)
        stream.write(name)
        date = tuple(list(self.date.timetuple())[:-3])
        date = struct.pack('hhhhhh', *date)
        stream.write(date)
        stream.write(ut.i2b(self.size))

    def load(self):
        stream = open(self.name, 'rb')
        self.data = stream.read()
        self.size = ut.get_file_size(self.name)
        self.date = ut.get_mod_date(self.name)

    def save(self, path):
        if (self.data.__class__.__name__ == 'bytes') or \
           (self.data.__class__.__name__ == 'bytearray'):
            path = os.path.join(path, self.name)
            stream = open(path, 'wb')
            stream.write(self.data)
            stream.close()
            date = time.mktime(self.date.timetuple())
            os.utime(path, (date, date))
        else:
            self.data.name = self.name
            self.data.save(path)

    def __repr__(self):
        return (
            f'\nclass: {self.__class__.__name__}\n'
            f'name: {self.name}\n'
            f'size: {self.size}\n'
            f'date: {self.date}\n'
        )