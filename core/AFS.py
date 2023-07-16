from io import BytesIO
from typing import io
import os, glob
import time, datetime
import struct
import re
import core.utils as ut
import core.common as cm
from colorama import Fore, Style
from core.AFL import *
from core.STPZ import *
from core.STPZ_LZ import *
from core.STPK import *

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
        ut.toggle_endian()
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
        ut.toggle_endian()

    def compress(self):
        for entry in self.entries:
            entry.compress()
        self.update_offsets()

    def decompress(self):
        for i in range(len(self.entries)):
            self.entries[i].decompress()

    def write(self, stream):
        if (ut.endian == 'big'):
            ut.toggle_endian()
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
            afl_object.add(entry.name)
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
            if (self.data[:4] == b'STPZ'):
                return
            ut.init_decomp_dir()
            temp_data_path = os.path.join(cm.decomp_path, self.name)
            stream = open(temp_data_path, 'wb')
            stream.write(self.data)
            stream.flush()

            stpz_object = STPZ()
            stpz_object.data = self.data
            stpz_path = stpz_object.compress(temp_data_path)
            stream = open(stpz_path, 'rb')
            self.data = stream.read()
            self.name = os.path.basename(stpz_path)
            self.size = len(self.data)
        except Exception as e:
            print(f"{Fore.YELLOW}WARNING: dbrb_compressor error for file {self.name}")
            print(f"Using LZ algorithm instead...{Style.RESET_ALL}")
            ut.toggle_endian()
            data_object = STPZ_LZ(self.name)
            stream = open(temp_data_path, 'rb')
            data_object.read(stream)
            data_object.compress()

            stream = BytesIO()
            data_object.write(stream)
            stream.seek(0)
            self.data = stream.read()

            name, ext = os.path.splitext(self.name)
            if (ext.endswith(".spr")):
                name += "_s"
            elif (ext.endswith(".vram")):
                name += "_v"
            elif (ext.endswith(".ioram")):
                name += "_i"
            ext = cm.ext_map['STPZ_LZ'][0]
            self.name = f"{name}{ext}"

            self.size = len(self.data)

            ut.toggle_endian()

    def decompress(self):
        try:
            ut.init_decomp_dir()
            temp_data_path = os.path.join(cm.decomp_path, self.name)
            stream = open(temp_data_path, 'wb')
            stream.write(self.data)
            stream.flush()

            try:
                data_object = STPZ()
                self.data = data_object.decompress(temp_data_path)
            except Exception as e:
                print(f"{Fore.YELLOW}WARNING: dbrb_compressor error for file {self.name}")
                print(f"Using LZ algorithm instead...{Style.RESET_ALL}")
                ut.toggle_endian()
                stream = open(temp_data_path, 'rb')
                data_tag = stream.read(4)
                data_tag = data_tag.replace(b'0', b'O')
                try:
                    data_object = eval(data_tag)()
                    data_object.read(stream)
                    self.data = data_object.decompress(True)
                except:
                    print(f"{Fore.RED}ERROR: couldn't decompress {self.name}")
                ut.toggle_endian()

            if hasattr(data_object, 'data'):
                self.data = data_object.data
            data_class_name = self.data.__class__.__name__
            name, ext = os.path.splitext(self.name)

            checkName = False
            if data_class_name != 'bytearray':
                self.data.date = self.date
                if (data_class_name in cm.ext_map):
                    ext = cm.ext_map[data_class_name][0]
                    self.name = f"{name}{ext}"
                else:
                    checkName = True
            else:
                checkName = True

            if (checkName):
                if (name.endswith("_s")):
                    name = name[:-2] + ".spr"
                elif (name.endswith("_v")):
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
        path = os.path.join(path, self.name)
        if (self.data.__class__.__name__ not in ['bytes', 'bytearray']):
            stream = BytesIO()
            self.data.write(stream)
            stream.seek(0)
            self.data = stream.read()
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
            f'date: {self.date}\n'
        )