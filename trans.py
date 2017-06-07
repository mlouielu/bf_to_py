import os, sys
from ir  import *
from opt import *

opts = {'contract':  opt_contract,
        'clearloop': opt_clearloop,
        'copyloop':  opt_copyloop,
        'multiloop': opt_multiloop,
        'offsetops': opt_offsetops,
        'cancelops': opt_cancel,}
optimizations = ['contract', 'clearloop',
                 'copyloop', 'multiloop',
                 'offsetops', 'cancelops']


def entry_point(argv):
    if len(argv) >= 3:
        filename  = argv[1]
        writename = argv[2]
    else:
        print("You must provide a brainfuck file!")
        print("You also need to name a file to write your PyCode to.")
        print("Usage: <trans.py> <input> <output>")
        return 1
    inp_file = os.open(filename, os.O_RDONLY, 0777)
    program = ''
    while True:
        read = os.read(inp_file, 4096)
        if not len(read):
            break
        program += read
    os.close(inp_file)
    ir = bf_to_ir(program)
    for x in optimizations:
        ir = opts[x](ir)
    py_code = ir_to_py(ir)
    writefile = open(writename, 'w')
    writefile.write(py_code)
    writefile.close()
    return 0

def targets(*args):
    return entry_point, None

if __name__ == '__main__':
    res = entry_point(sys.argv)
    sys.exit(res)
