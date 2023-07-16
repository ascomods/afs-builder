import os, sys

app_path = os.path.dirname(os.path.realpath(sys.argv[0]))
run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
temp_path = os.path.join(run_path, 'temp')
decomp_path = os.path.join(run_path, 'temp', 'decomp')

class_map = {
    b'SPR3': b'SPRP'
}

ext_map = {
    'SPRP': ['.spr'],
    'STPK': ['.pak', '.stpk'],
    'STPZ': ['.zpak', '.stpz'],
    'STPZ_LZ': ['.zpak', '.stpz']
}